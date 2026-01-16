# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import psycopg2
import psycopg2.extras
import os
import logging

from app.database import get_db_connection

logger = logging.getLogger(__name__)

def init_db():
    try:
        with get_db_connection() as (conn, cur):
            # Create submissions table with updated schema
            cur.execute('''
                CREATE TABLE IF NOT EXISTS ministry_submissions (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    email VARCHAR(255) DEFAULT '',
                    age_group VARCHAR(50),
                    gender VARCHAR(20),
                    state_in_life JSONB DEFAULT '[]'::jsonb,
                    interest JSONB,
                    situation JSONB DEFAULT '[]'::jsonb,
                    recommended_ministries JSONB DEFAULT '[]'::jsonb,
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
            
            # Fix email column constraint if it exists
            cur.execute("""
                SELECT is_nullable FROM information_schema.columns 
                WHERE table_name = 'ministry_submissions' AND column_name = 'email'
            """)
            result = cur.fetchone()
            if result and result[0] == 'NO':
                logger.info("Fixing email column constraint to allow empty values...")
                try:
                    cur.execute("ALTER TABLE ministry_submissions ALTER COLUMN email DROP NOT NULL")
                    cur.execute("ALTER TABLE ministry_submissions ALTER COLUMN email SET DEFAULT ''")
                    logger.info("Successfully updated email column to allow empty values")
                except Exception as e:
                    logger.error(f"Error updating email column: {e}")
                    logger.info("Email column constraint update failed - continuing with existing schema")
            
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
            if result and result[0] != 'jsonb':
                logger.info("Converting interest column to JSONB...")
                try:
                    cur.execute("""
                        ALTER TABLE ministry_submissions
                        ALTER COLUMN interest TYPE JSONB
                        USING
                            CASE
                                WHEN interest IS NULL OR interest = '' THEN '[]'::jsonb
                                WHEN interest::text LIKE '[%' THEN interest::jsonb
                                ELSE to_jsonb(interest)
                            END
                    """)
                    logger.info("Successfully updated interest column to JSONB type")
                except Exception as e:
                    logger.error(f"Error converting interest to JSONB: {e}")
                    logger.info("Keeping interest as VARCHAR for now - will work with existing data")
            
            # SAFE MIGRATION: Handle recommended_ministries column similarly if needed
            cur.execute("""
                SELECT data_type FROM information_schema.columns 
                WHERE table_name = 'ministry_submissions' AND column_name = 'recommended_ministries'
            """)
            result = cur.fetchone()
            if result and result[0] != 'jsonb':
                logger.info("Converting recommended_ministries column to JSONB...")
                try:
                    cur.execute("""
                        ALTER TABLE ministry_submissions
                        ALTER COLUMN recommended_ministries TYPE JSONB
                        USING
                            CASE
                                WHEN recommended_ministries IS NULL OR recommended_ministries = '' THEN '[]'::jsonb
                                WHEN recommended_ministries::text LIKE '[%' THEN recommended_ministries::jsonb
                                ELSE to_jsonb(recommended_ministries)
                            END
                    """)
                    logger.info("Successfully updated recommended_ministries column to JSONB type")
                except Exception as e:
                    logger.error(f"Error converting recommended_ministries to JSONB: {e}")
                    logger.info("Keeping recommended_ministries as TEXT for now - will work with existing data")
            
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
            
            logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise the exception - let the app continue
        logger.info("Continuing with existing database schema")
