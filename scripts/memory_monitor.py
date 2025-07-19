#!/usr/bin/env python3
"""
Memory monitoring script for the St. Edward Ministry Finder application.
This script helps track memory usage and identify potential memory leaks.
"""

import os
import sys
import time
import psutil
import logging
from datetime import datetime
import json

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cache import get_cache_stats
from app.monitoring import app_monitor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_memory_info():
    """Get detailed memory information"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # Get system memory info
        system_memory = psutil.virtual_memory()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'process': {
                'rss_mb': round(memory_info.rss / (1024 * 1024), 2),
                'vms_mb': round(memory_info.vms / (1024 * 1024), 2),
                'percent': round(memory_percent, 2)
            },
            'system': {
                'total_gb': round(system_memory.total / (1024 * 1024 * 1024), 2),
                'available_gb': round(system_memory.available / (1024 * 1024 * 1024), 2),
                'percent': round(system_memory.percent, 2)
            }
        }
    except Exception as e:
        logger.error(f"Error getting memory info: {e}")
        return None

def get_app_metrics():
    """Get application-specific metrics"""
    try:
        # Get cache stats
        cache_stats = get_cache_stats()
        
        # Get monitoring metrics
        monitoring_metrics = app_monitor.get_metrics()
        
        return {
            'cache': cache_stats,
            'monitoring': monitoring_metrics.get('application', {}).get('monitoring_data_size', {})
        }
    except Exception as e:
        logger.error(f"Error getting app metrics: {e}")
        return {}

def monitor_memory(interval=60, duration=None):
    """
    Monitor memory usage for a specified duration
    
    Args:
        interval: Check interval in seconds (default: 60)
        duration: Total monitoring duration in seconds (None for infinite)
    """
    logger.info(f"Starting memory monitoring (interval: {interval}s, duration: {duration}s)")
    
    start_time = time.time()
    check_count = 0
    
    while True:
        try:
            check_count += 1
            current_time = time.time()
            
            # Check if we should stop
            if duration and (current_time - start_time) > duration:
                logger.info(f"Monitoring completed after {duration} seconds")
                break
            
            # Get memory info
            memory_info = get_memory_info()
            if memory_info:
                app_metrics = get_app_metrics()
                
                # Log memory usage
                logger.info(f"Check #{check_count} - "
                          f"Process: {memory_info['process']['rss_mb']}MB "
                          f"({memory_info['process']['percent']:.1f}%) | "
                          f"System: {memory_info['system']['percent']:.1f}% | "
                          f"Cache: {app_metrics.get('cache', {}).get('memory_usage_mb', 'N/A')}MB")
                
                # Check for high memory usage
                if memory_info['process']['percent'] > 80:
                    logger.warning(f"HIGH MEMORY USAGE: {memory_info['process']['percent']:.1f}%")
                
                if memory_info['system']['percent'] > 90:
                    logger.warning(f"HIGH SYSTEM MEMORY: {memory_info['system']['percent']:.1f}%")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            logger.info("Memory monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in memory monitoring: {e}")
            time.sleep(interval)

def print_current_status():
    """Print current memory status"""
    memory_info = get_memory_info()
    app_metrics = get_app_metrics()
    
    if memory_info:
        print("\n=== MEMORY STATUS ===")
        print(f"Timestamp: {memory_info['timestamp']}")
        print(f"Process Memory: {memory_info['process']['rss_mb']}MB ({memory_info['process']['percent']:.1f}%)")
        print(f"System Memory: {memory_info['system']['percent']:.1f}%")
        print(f"Cache Memory: {app_metrics.get('cache', {}).get('memory_usage_mb', 'N/A')}MB")
        
        if app_metrics.get('monitoring'):
            print(f"Monitoring Data: {app_metrics['monitoring']}")
        
        print("====================\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory monitoring for St. Edward Ministry Finder')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')
    parser.add_argument('--duration', type=int, help='Total monitoring duration in seconds (default: infinite)')
    parser.add_argument('--status', action='store_true', help='Print current status and exit')
    
    args = parser.parse_args()
    
    if args.status:
        print_current_status()
    else:
        monitor_memory(interval=args.interval, duration=args.duration) 