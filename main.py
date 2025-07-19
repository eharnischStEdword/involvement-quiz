# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import os
import logging
import threading
import time
import requests
import pytz
from datetime import datetime
import json

from flask import jsonify
from app import create_app
from app.database import get_db_connection, close_connection_pool
from app.ministries import MINISTRY_DATA
from app.config import Config

# Create the Flask application using the factory pattern
app = create_app()
config = Config.get_config()

# Set up logging
logger = logging.getLogger(__name__)

def keep_alive():
    """Enhanced keep-alive service to prevent Render from sleeping"""
    time.sleep(60)  # Wait 1 minute before starting
    
    while True:
        try:
            central = pytz.timezone('US/Central')
            now = datetime.now(central)
            
            # More aggressive during business hours, less aggressive at night
            if 6 <= now.hour <= 23:  # Extended hours
                interval = 300  # 5 minutes during business hours
                url = os.environ.get('RENDER_EXTERNAL_URL', 'https://involvement-quiz.onrender.com')
                
                # Ping single endpoint for efficiency
                try:
                    response = requests.get(f'{url}/api/health', timeout=10)
                    logger.info(f"Keep-alive ping to {url}/api/health - Status: {response.status_code}")
                    # Explicitly close response to free memory
                    response.close()
                except Exception as e:
                    logger.warning(f"Keep-alive ping failed: {e}")
            else:
                interval = 900  # 15 minutes during off-hours
                logger.info("Off-hours mode - reduced ping frequency")
            
            time.sleep(interval)
            
        except Exception as e:
            logger.error(f"Keep-alive service error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

def auto_migrate_ministries():
    """Auto-migrate ministry data to database on startup"""
    try:
        logger.info("Starting ministry migration...")
        
        with get_db_connection() as (conn, cur):
            # Check if ministries table is empty
            cur.execute("SELECT COUNT(*) FROM ministries")
            count = cur.fetchone()[0]
            
            if count == 0:
                logger.info("Ministries table is empty, migrating data...")
                
                # Insert all ministries from MINISTRY_DATA
                for key, ministry in MINISTRY_DATA.items():
                    cur.execute('''
                        INSERT INTO ministries 
                        (ministry_key, name, description, details, age_groups, 
                         genders, states, interests, situations, active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (ministry_key) DO NOTHING
                    ''', (
                        key,
                        ministry.get('name'),
                        ministry.get('description', ''),
                        ministry.get('details', ''),
                        json.dumps(ministry.get('age', [])),
                        json.dumps(ministry.get('gender', [])),
                        json.dumps(ministry.get('state', [])),
                        json.dumps(ministry.get('interest', [])),
                        json.dumps(ministry.get('situation', [])),
                        True
                    ))
                
                logger.info(f"Successfully migrated {len(MINISTRY_DATA)} ministries to database")
            else:
                logger.info(f"Ministries table already has {count} entries, skipping migration")
                
                # Ensure mass ministry is always active
                mass_data = MINISTRY_DATA.get('mass')
                if mass_data:
                    cur.execute(
                        '''
                        INSERT INTO ministries (ministry_key, name, description, details, age_groups, genders, states, interests, situations, active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                        ON CONFLICT (ministry_key)
                        DO UPDATE SET active = TRUE
                        ''',
                        ( 'mass', 
                          mass_data.get('name'),
                          mass_data.get('description', ''),
                          mass_data.get('details', ''),
                          json.dumps(mass_data.get('age', [])),
                          json.dumps(mass_data.get('gender', [])),
                          json.dumps(mass_data.get('state', [])),
                          json.dumps(mass_data.get('interest', [])),
                          json.dumps(mass_data.get('situation', []))
                        )
                    )
                    logger.info("Ensured 'Come to Mass' ministry is present and active")
                
    except Exception as e:
        logger.error(f"Ministry migration failed: {e}")

# Auto-migrate ministries on startup
auto_migrate_ministries()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return {'error': 'Internal server error'}, 500

@app.route('/health')
def health_check():
    """Health check endpoint for keep-alive service"""
    try:
        # Test database connection
        with get_db_connection() as (conn, cur):
            cur.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'St. Edward Ministry Finder'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500



# Start keep-alive service (only in production)
if config['IS_PRODUCTION']:
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        try:
            threading.Thread(target=keep_alive, daemon=True).start()
            logger.info("Keep-alive service started for production")
        except Exception as e:
            logger.error(f"Failed to start keep-alive service: {e}")
else:
    logger.info("Local development mode - keep-alive service disabled")

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Ensure connection pool is closed on app shutdown"""
    if exception:
        logger.error(f"App teardown due to exception: {exception}")

if __name__ == '__main__':
    try:
        logger.info("Starting St. Edward Ministry Finder application")
        app.run(
            debug=config['DEBUG'],  # Use config for debug mode
            host='0.0.0.0', 
            port=int(os.environ.get('PORT', 5000))
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        close_connection_pool()
