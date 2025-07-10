"""
Add ministries table migration
Run this script to create the ministries table and migrate existing data
"""
import psycopg2
import json
import logging
from datetime import datetime
from app.database import get_db_connection
from app.ministries import MINISTRY_DATA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_ministries_table():
    """Create the ministries table and audit table"""
    try:
        with get_db_connection() as (conn, cur):
            # Create ministries table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS ministries (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    details TEXT,
                    age_groups TEXT[],
                    genders TEXT[],
                    states TEXT[],
                    interests TEXT[],
                    situations TEXT[],
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by VARCHAR(100) DEFAULT 'migration'
                )
            ''')
            
            # Create audit table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS ministry_audit (
                    id SERIAL PRIMARY KEY,
                    ministry_id INTEGER REFERENCES ministries(id),
                    action VARCHAR(20),
                    changed_by VARCHAR(100),
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    changes JSONB
                )
            ''')
            
            # Create index for faster lookups
            cur.execute('CREATE INDEX IF NOT EXISTS idx_ministries_key ON ministries(key)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_ministries_active ON ministries(active)')
            
            conn.commit()
            logger.info("Tables created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def migrate_ministry_data():
    """Migrate existing ministry data to database"""
    try:
        with get_db_connection() as (conn, cur):
            migrated = 0
            
            for key, ministry in MINISTRY_DATA.items():
                # Convert data types
                age_groups = ministry.get('age', [])
                genders = ministry.get('gender', [])
                states = ministry.get('state', [])
                interests = ministry.get('interest', [])
                situations = ministry.get('situation', [])
                
                # Insert ministry
                cur.execute('''
                    INSERT INTO ministries 
                    (key, name, description, details, age_groups, genders, states, interests, situations)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        details = EXCLUDED.details,
                        age_groups = EXCLUDED.age_groups,
                        genders = EXCLUDED.genders,
                        states = EXCLUDED.states,
                        interests = EXCLUDED.interests,
                        situations = EXCLUDED.situations,
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = 'migration'
                ''', (
                    key,
                    ministry.get('name', ''),
                    ministry.get('description', ''),
                    ministry.get('details', ''),
                    age_groups,
                    genders,
                    states,
                    interests,
                    situations
                ))
                
                migrated += 1
                logger.info(f"Migrated ministry: {key}")
            
            conn.commit()
            logger.info(f"Successfully migrated {migrated} ministries")
            return True
            
    except Exception as e:
        logger.error(f"Error migrating data: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('SELECT COUNT(*) FROM ministries WHERE active = TRUE')
            count = cur.fetchone()[0]
            
            cur.execute('SELECT key, name FROM ministries ORDER BY key LIMIT 5')
            samples = cur.fetchall()
            
            logger.info(f"Total active ministries in database: {count}")
            logger.info(f"Sample ministries: {samples}")
            
            return count > 0
            
    except Exception as e:
        logger.error(f"Error verifying migration: {e}")
        return False

if __name__ == '__main__':
    logger.info("Starting ministry database migration...")
    
    # Step 1: Create tables
    if not create_ministries_table():
        logger.error("Failed to create tables. Aborting migration.")
        exit(1)
    
    # Step 2: Migrate data
    if not migrate_ministry_data():
        logger.error("Failed to migrate data. Tables created but empty.")
        exit(1)
    
    # Step 3: Verify
    if verify_migration():
        logger.info("Migration completed successfully!")
    else:
        logger.warning("Migration completed but verification failed.")