from flask import Flask
from flask_cors import CORS
import os
import logging
import threading
import time
import requests
import pytz
from datetime import datetime

from app.models import init_db
from app.routes import register_routes

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def keep_alive():
    """Ping the service every 10 minutes to prevent sleeping"""
    time.sleep(60)  # Wait 1 minute before starting to let app fully start
    
    while True:
        try:
            time.sleep(600)  # Wait 10 minutes
            # Only ping during reasonable hours (7 AM - 11 PM Central Time)
            central = pytz.timezone('US/Central')
            now = datetime.now(central)
            
            # Only keep alive during extended business hours
            if 7 <= now.hour <= 23:  # 7 AM to 11 PM Central
                url = os.environ.get('RENDER_EXTERNAL_URL', 'https://involvement-quiz.onrender.com')
                response = requests.get(f'{url}/health', timeout=30)
                logger.info(f"Keep-alive ping sent - Status: {response.status_code}")
            else:
                logger.info("Outside business hours, allowing sleep")
        except Exception as e:
            logger.error(f"Keep-alive failed: {e}")
            # Continue the loop even if ping fails

# Initialize database on startup
try:
    init_db()
    logger.info("Database initialized on startup")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

# Register all routes
register_routes(app)

# Start keep-alive service (only in production)
if os.environ.get('DATABASE_URL'):  # Only run keep-alive in production
    if not os.environ.get('WERKZEUG_RUN_MAIN'):  # Prevent duplicate threads in debug mode
        try:
            threading.Thread(target=keep_alive, daemon=True).start()
            logger.info("Keep-alive service started for production")
        except Exception as e:
            logger.error(f"Failed to start keep-alive service: {e}")
else:
    logger.info("Local development mode - keep-alive service disabled")

if __name__ == '__main__':
    try:
        logger.info("Starting St. Edward Ministry Finder application")
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
