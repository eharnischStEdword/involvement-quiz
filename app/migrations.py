# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import logging
from app.database import get_db_connection
from app.logging_config import get_logger

logger = get_logger(__name__)

class MigrationManager:
    """Simple database migration manager"""
    
    def __init__(self):
        self.migrations = [
            {
                'id': 1,
                'name': 'create_ministry_submissions_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS ministry_submissions (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255),
                        age_group VARCHAR(50),
                        gender VARCHAR(50),
                        state_in_life TEXT,
                        interest TEXT,
                        situation TEXT,
                        recommended_ministries TEXT,
                        ip_address VARCHAR(45),
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''
            },
            {
                'id': 2,
                'name': 'create_ministries_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS ministries (
                        id SERIAL PRIMARY KEY,
                        ministry_key VARCHAR(100) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        details TEXT,
                        age_groups TEXT,
                        genders TEXT,
                        states TEXT,
                        interests TEXT,
                        situations TEXT,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''
            },
            {
                'id': 3,
                'name': 'add_updated_at_to_ministries',
                'sql': '''
                    ALTER TABLE ministries 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                '''
            },
            {
                'id': 4,
                'name': 'add_indexes_for_performance',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_ministry_submissions_submitted_at 
                    ON ministry_submissions(submitted_at);
                    
                    CREATE INDEX IF NOT EXISTS idx_ministry_submissions_ip_address 
                    ON ministry_submissions(ip_address);
                    
                    CREATE INDEX IF NOT EXISTS idx_ministries_active 
                    ON ministries(active);
                    
                    CREATE INDEX IF NOT EXISTS idx_ministries_ministry_key 
                    ON ministries(ministry_key);
                '''
            }
        ]
    
    def create_migrations_table(self):
        """Create the migrations tracking table"""
        try:
            with get_db_connection() as (conn, cur):
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS migrations (
                        id SERIAL PRIMARY KEY,
                        migration_id INTEGER UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("Migrations table created/verified")
        except Exception as e:
            logger.error(f"Failed to create migrations table: {e}")
            raise
    
    def get_applied_migrations(self):
        """Get list of applied migration IDs"""
        try:
            with get_db_connection() as (conn, cur):
                cur.execute('SELECT migration_id FROM migrations ORDER BY migration_id')
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def apply_migration(self, migration):
        """Apply a single migration"""
        try:
            with get_db_connection() as (conn, cur):
                # Execute the migration SQL
                cur.execute(migration['sql'])
                
                # Record the migration
                cur.execute('''
                    INSERT INTO migrations (migration_id, name)
                    VALUES (%s, %s)
                ''', (migration['id'], migration['name']))
                
                conn.commit()
                logger.info(f"Applied migration {migration['id']}: {migration['name']}")
                
        except Exception as e:
            logger.error(f"Failed to apply migration {migration['id']}: {e}")
            raise
    
    def run_migrations(self):
        """Run all pending migrations"""
        try:
            # Ensure migrations table exists
            self.create_migrations_table()
            
            # Get applied migrations
            applied_migrations = self.get_applied_migrations()
            
            # Find pending migrations
            pending_migrations = [
                m for m in self.migrations 
                if m['id'] not in applied_migrations
            ]
            
            if not pending_migrations:
                logger.info("No pending migrations")
                return
            
            logger.info(f"Running {len(pending_migrations)} pending migrations")
            
            # Apply pending migrations
            for migration in pending_migrations:
                self.apply_migration(migration)
            
            logger.info("All migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

def run_migrations():
    """Convenience function to run migrations"""
    manager = MigrationManager()
    manager.run_migrations() 