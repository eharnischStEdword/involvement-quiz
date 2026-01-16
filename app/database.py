# © 2024–2026 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import os
import logging
import psycopg2
import psycopg2.pool
import psycopg2.extras
from contextlib import contextmanager
from threading import Lock

logger = logging.getLogger(__name__)

# Thread-safe connection pool instance
_connection_pool = None
_pool_pid = None
_pool_lock = Lock()

def init_connection_pool(minconn=2, maxconn=10):
    """Initialize the connection pool"""
    global _connection_pool, _pool_pid
    
    with _pool_lock:
        current_pid = os.getpid()
        
        # If pool exists but PID is different, we've forked
        if _connection_pool is not None and _pool_pid != current_pid:
            logger.info(f"Detected process fork (PID {_pool_pid} -> {current_pid}), re-initializing pool")
            # Don't call closeall() on inherited pool as it can interfere with other processes
            _connection_pool = None
            
        # Return existing pool if already initialized for this PID
        if _connection_pool is not None:
            return _connection_pool
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        
        try:
            if DATABASE_URL:
                # Production database
                _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn,
                    maxconn,
                    DATABASE_URL,
                    sslmode='require',
                    connect_timeout=10,  # 10 second connection timeout
                    options='-c statement_timeout=30000'  # 30 second query timeout
                )
                logger.info(f"Initialized production connection pool (min={minconn}, max={maxconn})")
            else:
                # Local development
                _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn,
                    maxconn,
                    host=os.environ.get('DB_HOST', 'localhost'),
                    database=os.environ.get('DB_NAME', 'st_edward_ministries'),
                    user=os.environ.get('DB_USER', 'your_username'),
                    password=os.environ.get('DB_PASSWORD', 'your_password'),
                    connect_timeout=10,  # 10 second connection timeout
                    options='-c statement_timeout=30000'  # 30 second query timeout
                )
                logger.info(f"Initialized local connection pool (min={minconn}, max={maxconn})")
                
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
            
        _pool_pid = current_pid
            
    return _connection_pool

def get_connection_pool():
    """Get or create the connection pool"""
    global _connection_pool, _pool_pid
    
    current_pid = os.getpid()
    
    # Check if pool needs initialization or re-initialization after fork
    if _connection_pool is None or _pool_pid != current_pid:
        init_connection_pool()
        
    return _connection_pool

@contextmanager
def get_db_connection(cursor_factory=None):
    """
    Context manager for database connections with automatic cleanup
    
    Usage:
        with get_db_connection() as (conn, cur):
            cur.execute("SELECT * FROM table")
            results = cur.fetchall()
    """
    pool = get_connection_pool()
    if pool is None:
        raise Exception("Database connection pool not initialized")
    
    conn = None
    cur = None
    
    try:
        # Get connection from pool
        conn = pool.getconn()
        
        # Verify connection is alive and healthy
        is_healthy = False
        try:
            if not conn.closed:
                # poll() returns None if healthy, or raises error
                conn.poll()
                is_healthy = True
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            is_healthy = False

        if not is_healthy:
            logger.warning("Retrieved unhealthy connection from pool, attempting to get a new one")
            try:
                pool.putconn(conn, close=True)
            except:
                pass
            conn = pool.getconn()
            
        if cursor_factory:
            cur = conn.cursor(cursor_factory=cursor_factory)
        else:
            cur = conn.cursor()
            
        yield conn, cur
        
        # Commit if no exception occurred
        if not conn.closed:
            conn.commit()
        
    except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
        # These errors often indicate a connection problem
        if conn:
            try:
                conn.rollback()
            except:
                pass
        logger.error(f"Database connection error: {e}")
        # Discard broken connection
        if conn and pool:
            pool.putconn(conn, close=True)
            conn = None
        raise
        
    except psycopg2.Error as e:
        # Rollback on other database errors
        if conn and not conn.closed:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
        
    except Exception as e:
        # Rollback on any other errors
        if conn and not conn.closed:
            conn.rollback()
        logger.error(f"Unexpected error: {e}")
        raise
        
    finally:
        # Clean up cursor and return connection to pool
        if cur:
            try:
                cur.close()
            except:
                pass
        if conn and pool:
            # Return healthy connection to pool
            pool.putconn(conn, close=conn.closed)

def close_connection_pool():
    """Close all connections in the pool"""
    global _connection_pool
    
    with _pool_lock:
        if _connection_pool:
            _connection_pool.closeall()
            _connection_pool = None
            logger.info("Connection pool closed")

def execute_query(query, params=None, fetch_one=False, cursor_factory=None):
    """
    Helper function for simple queries
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        fetch_one: If True, return single row, else return all rows
        cursor_factory: Optional cursor factory (e.g., RealDictCursor)
        
    Returns:
        Query results or None
    """
    with get_db_connection(cursor_factory=cursor_factory) as (conn, cur):
        cur.execute(query, params)
        
        if cur.description is None:
            # Query doesn't return results (INSERT, UPDATE, DELETE)
            return None
            
        if fetch_one:
            return cur.fetchone()
        else:
            return cur.fetchall()

def execute_many(query, params_list):
    """
    Execute the same query multiple times with different parameters
    
    Args:
        query: SQL query string
        params_list: List of parameter tuples
        
    Returns:
        Number of affected rows
    """
    with get_db_connection() as (conn, cur):
        cur.executemany(query, params_list)
        return cur.rowcount

# CSV Export specific function
def get_submissions_for_csv(date_from=None, date_to=None):
    """
    Get submissions for CSV export with dynamic column handling
    
    Args:
        date_from: Optional start date filter
        date_to: Optional end date filter
        
    Returns:
        Tuple of (headers, rows)
    """
    query = """
        SELECT * FROM ministry_submissions
        WHERE 1=1
    """
    params = []
    
    if date_from:
        query += " AND submitted_at >= %s"
        params.append(date_from)
        
    if date_to:
        query += " AND submitted_at <= %s"
        params.append(date_to)
        
    query += " ORDER BY submitted_at DESC"
    
    with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
        cur.execute(query, params)
        
        # Get column names dynamically from cursor description
        headers = [desc[0] for desc in cur.description]
        
        # Fetch all rows
        rows = cur.fetchall()
        
        return headers, rows
