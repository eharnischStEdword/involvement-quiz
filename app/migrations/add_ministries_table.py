#!/usr/bin/env python3
import sys
import os
import json
import logging
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import get_db_connection
from app.ministries import MINISTRY_DATA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_ministries_table():
    """Create the ministries table"""
    with get_db_connection() as (conn, cur):
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ministries (
                id SERIAL PRIMARY KEY,
                ministry_key VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                details TEXT,
                age_groups JSONB DEFAULT '[]',
                genders JSONB DEFAULT '[]',
                states JSONB DEFAULT '[]',
                interests JSONB DEFAULT '[]',
                situations JSONB DEFAULT '[]',
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Created ministries table")

def migrate_ministry_data():
    """Migrate MINISTRY_DATA to database"""
    with get_db_connection() as (conn, cur):
        inserted = 0
        updated = 0
        
        for key, ministry in MINISTRY_DATA.items():
            # Check if ministry exists
            cur.execute("SELECT id FROM ministries WHERE ministry_key = %s", (key,))
            exists = cur.fetchone()
            
            if exists:
                # Update existing
                cur.execute('''
                    UPDATE ministries SET
                        name = %s,
                        description = %s,
                        details = %s,
                        age_groups = %s,
                        genders = %s,
                        states = %s,
                        interests = %s,
                        situations = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE ministry_key = %s
                ''', (
                    ministry['name'],
                    ministry.get('description', ''),
                    ministry.get('details', ''),
                    json.dumps(ministry.get('age', [])),
                    json.dumps(ministry.get('gender', [])),
                    json.dumps(ministry.get('state', [])),
                    json.dumps(ministry.get('interest', [])),
                    json.dumps(ministry.get('situation', [])),
                    key
                ))
                updated += 1
            else:
                # Insert new
                cur.execute('''
                    INSERT INTO ministries 
                    (ministry_key, name, description, details, age_groups, genders, states, interests, situations)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    key,
                    ministry['name'],
                    ministry.get('description', ''),
                    ministry.get('details', ''),
                    json.dumps(ministry.get('age', [])),
                    json.dumps(ministry.get('gender', [])),
                    json.dumps(ministry.get('state', [])),
                    json.dumps(ministry.get('interest', [])),
                    json.dumps(ministry.get('situation', []))
                ))
                inserted += 1
        
        logger.info(f"Migration complete: {inserted} inserted, {updated} updated")

def verify_migration():
    """Verify migration success"""
    with get_db_connection() as (conn, cur):
        cur.execute("SELECT COUNT(*) FROM ministries")
        count = cur.fetchone()[0]
        logger.info(f"Total ministries in database: {count}")
        
        cur.execute("SELECT ministry_key, name FROM ministries LIMIT 5")
        samples = cur.fetchall()
        logger.info("Sample ministries:")
        for key, name in samples:
            logger.info(f"  - {key}: {name}")

if __name__ == "__main__":
    try:
        logger.info("Starting ministry migration...")
        create_ministries_table()
        migrate_ministry_data()
        verify_migration()
        logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
