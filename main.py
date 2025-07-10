from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman
from flask_caching import Cache
import os
import logging
import threading
import time
import requests
import pytz
from datetime import datetime
import json

from app.models import init_db
from app.database import init_connection_pool, close_connection_pool, get_db_connection
from app.ministries import MINISTRY_DATA
from app.blueprints.public import public_bp
from app.blueprints.api import api_bp
from app.blueprints.admin import admin_bp
from app.blueprints.ministry_admin import ministry_admin_bp

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Configure Talisman for HTTPS (disable in development)
if os.environ.get('DATABASE_URL'):  # Production
    Talisman(app, force_https=True, strict_transport_security=True)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def keep_alive():
    """Ping the service every 10 minutes to prevent sleeping"""
    time.sleep(60)
    
    while True:
        try:
            time.sleep(600)
            central = pytz.timezone('US/Central')
            now = datetime.now(central)
            
            if 7 <= now.hour <= 23:
                url = os.environ.get('RENDER_EXTERNAL_URL', 'https://involvement-quiz.onrender.com')
                response = requests.get(f'{url}/api/health', timeout=30)
                logger.info(f"Keep-alive ping sent - Status: {response.status_code}")
            else:
                logger.info("Outside business hours, allowing sleep")
        except Exception as e:
            logger.error(f"Keep-alive failed: {e}")

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
                
    except Exception as e:
        logger.error(f"Ministry migration failed: {e}")

# Initialize database and connection pool on startup
try:
    init_db()
    init_connection_pool()
    logger.info("Database and connection pool initialized on startup")
    
    # Auto-migrate ministries
    auto_migrate_ministries()
    
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(ministry_admin_bp)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return {'error': 'Internal server error'}, 500

# Start keep-alive service (only in production)
if os.environ.get('DATABASE_URL'):
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
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        close_connection_pool()
