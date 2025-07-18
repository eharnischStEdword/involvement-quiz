#!/usr/bin/env python3
"""
External monitoring script for St. Edward Ministry Finder
Run this script on a separate service (like a Raspberry Pi, VPS, or cloud function)
to keep your Render.com service active.

Usage:
    python monitor.py
"""

import requests
import time
import logging
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
RENDER_URL = "https://involvement-quiz.onrender.com"
PING_INTERVAL = 300  # 5 minutes
TIMEOUT = 30

def ping_service():
    """Ping the Render service to keep it alive"""
    endpoints = [
        f"{RENDER_URL}/health",
        f"{RENDER_URL}/api/health", 
        f"{RENDER_URL}/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=TIMEOUT)
            if response.status_code == 200:
                logger.info(f"✅ Successfully pinged {endpoint}")
                return True
            else:
                logger.warning(f"⚠️  {endpoint} returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to ping {endpoint}: {e}")
            continue
    
    return False

def main():
    """Main monitoring loop"""
    logger.info("🚀 Starting St. Edward Ministry Finder monitor")
    logger.info(f"📡 Monitoring: {RENDER_URL}")
    logger.info(f"⏰ Ping interval: {PING_INTERVAL} seconds")
    
    consecutive_failures = 0
    max_failures = 5
    
    while True:
        try:
            # Get current time in Central timezone
            central = pytz.timezone('US/Central')
            now = datetime.now(central)
            
            # More aggressive during business hours
            if 6 <= now.hour <= 23:
                current_interval = PING_INTERVAL
                logger.info(f"🌅 Business hours mode - pinging every {current_interval} seconds")
            else:
                current_interval = PING_INTERVAL * 2  # 10 minutes during off-hours
                logger.info(f"🌙 Off-hours mode - pinging every {current_interval} seconds")
            
            # Ping the service
            success = ping_service()
            
            if success:
                consecutive_failures = 0
                logger.info(f"✅ Service is healthy at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            else:
                consecutive_failures += 1
                logger.error(f"❌ Service ping failed ({consecutive_failures}/{max_failures})")
                
                if consecutive_failures >= max_failures:
                    logger.critical("🚨 Too many consecutive failures - service may be down!")
                    # You could add email/SMS notifications here
            
            # Wait before next ping
            time.sleep(current_interval)
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main() 