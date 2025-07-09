import psycopg2
import psycopg2.extras
import os
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            logger.info("Connected to production database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to production database: {e}")
            raise
    else:
        # Local development
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='st_edward_ministries',
                user='your_username',
                password='your_password'
            )
            logger.info("Connected to local database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to local database: {e}")
            raise

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create submissions table with updated schema
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ministry_submissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) NOT NULL,
                age_group VARCHAR(50),
                gender VARCHAR(20),
                state_in_life JSONB DEFAULT '[]'::jsonb,
                interest VARCHAR(50),
                situation JSONB DEFAULT '[]'::jsonb,
                recommended_ministries TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45)
            )
        ''')
        
        # Add situation column if it doesn't exist
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'situation'
        """)
        if not cur.fetchone():
            cur.execute("ALTER TABLE ministry_submissions ADD COLUMN situation JSONB DEFAULT '[]'::jsonb")
            logger.info("Added situation column to ministry_submissions table")
        
        # Add ip_address column if it doesn't exist
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'ip_address'
        """)
        if not cur.fetchone():
            cur.execute("ALTER TABLE ministry_submissions ADD COLUMN ip_address VARCHAR(45)")
            logger.info("Added ip_address column to ministry_submissions table")
        
        # SAFE MIGRATION: Update state_in_life column to be JSONB if it's not already
        cur.execute("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'state_in_life'
        """)
        result = cur.fetchone()
        if result and result[0] != 'jsonb':
            logger.info("Converting state_in_life column to JSONB...")
            
            # Safe conversion: wrap existing string values in JSON arrays
            try:
                # First, handle NULL values
                cur.execute("""
                    UPDATE ministry_submissions 
                    SET state_in_life = '[]'::jsonb 
                    WHERE state_in_life IS NULL OR state_in_life = ''
                """)
                
                # Then convert non-empty string values to JSON arrays
                cur.execute("""
                    UPDATE ministry_submissions 
                    SET state_in_life = ('["' || state_in_life || '"]')::jsonb 
                    WHERE state_in_life IS NOT NULL 
                    AND state_in_life != '' 
                    AND state_in_life !~ '^\\[.*\\]$'
                """)
                
                # Now safely convert the column type
                cur.execute("""
                    ALTER TABLE ministry_submissions 
                    ALTER COLUMN state_in_life TYPE JSONB 
                    USING COALESCE(state_in_life::jsonb, '[]'::jsonb)
                """)
                
                logger.info("Successfully updated state_in_life column to JSONB type")
                
            except Exception as e:
                logger.error(f"Error converting state_in_life to JSONB: {e}")
                # If conversion fails, just ensure the column exists as VARCHAR for now
                logger.info("Keeping state_in_life as VARCHAR for now - will work with existing data")
        
        # SAFE MIGRATION: Handle interest column similarly if needed
        cur.execute("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'interest'
        """)
        result = cur.fetchone()
        if result and result[0] == 'character varying':
            logger.info("Interest column is VARCHAR - this is fine for backward compatibility")
        
        # Create ministries table for easier management
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ministries (
                id SERIAL PRIMARY KEY,
                ministry_key VARCHAR(100) UNIQUE,
                name VARCHAR(255),
                description TEXT,
                details TEXT,
                age_groups TEXT,
                genders TEXT,
                states TEXT,
                interests TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise the exception - let the app continue
        logger.info("Continuing with existing database schema")
