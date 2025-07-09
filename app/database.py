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
_pool_lock = Lock()

def init_connection_pool(minconn=2, maxconn=10):
    """Initialize the connection pool"""
    global _connection_pool
    
    with _pool_lock:
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
                    sslmode='require'
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
                    password=os.environ.get('DB_PASSWORD', 'your_password')
                )
                logger.info(f"Initialized local connection pool (min={minconn}, max={maxconn})")
                
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
            
    return _connection_pool

def get_connection_pool():
    """Get or create the connection pool"""
    global _connection_pool
    
    if _connection_pool is None:
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
    conn = None
    cur = None
    
    try:
        # Get connection from pool
        conn = pool.getconn()
        if cursor_factory:
            cur = conn.cursor(cursor_factory=cursor_factory)
        else:
            cur = conn.cursor()
            
        yield conn, cur
        
        # Commit if no exception occurred
        conn.commit()
        
    except psycopg2.Error as e:
        # Rollback on database errors
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
        
    except Exception as e:
        # Rollback on any other errors
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error: {e}")
        raise
        
    finally:
        # Clean up cursor and return connection to pool
        if cur:
            cur.close()
        if conn:
            pool.putconn(conn)

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
