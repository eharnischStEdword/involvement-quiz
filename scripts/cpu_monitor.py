#!/usr/bin/env python3
"""
Simple CPU monitoring script to track performance improvements
Run this script to monitor CPU usage over time
"""

import time
import psutil
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def monitor_cpu():
    """Monitor CPU usage and log high usage periods"""
    logger.info("Starting CPU monitoring...")
    
    high_cpu_count = 0
    total_checks = 0
    
    while True:
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1.0)
            total_checks += 1
            
            # Log high CPU usage
            if cpu_percent > 80:
                high_cpu_count += 1
                logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
            elif cpu_percent > 60:
                logger.info(f"Moderate CPU usage: {cpu_percent:.1f}%")
            else:
                logger.info(f"Normal CPU usage: {cpu_percent:.1f}%")
            
            # Log summary every 10 checks
            if total_checks % 10 == 0:
                high_cpu_rate = (high_cpu_count / total_checks) * 100
                logger.info(f"Summary: {total_checks} checks, {high_cpu_count} high CPU periods ({high_cpu_rate:.1f}%)")
            
            # Sleep for 5 minutes between checks
            time.sleep(300)
            
        except KeyboardInterrupt:
            logger.info("CPU monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"CPU monitoring error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_cpu() 