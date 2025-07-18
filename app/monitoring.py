# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from app.logging_config import get_logger
from app.cache import cache_manager, get_cache_stats

logger = get_logger(__name__)

class ApplicationMonitor:
    """Application performance monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_counts = {}
        self.error_counts = {}
        self.response_times = []
        self.max_response_times = 100  # Keep last 100 response times
        
        # Performance thresholds
        self.slow_request_threshold = 2.0  # seconds
        self.error_rate_threshold = 0.1  # 10% error rate
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background monitoring thread"""
        def monitor_loop():
            while True:
                try:
                    self._check_system_health()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Background monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Application monitoring started")
    
    def record_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Record a request for monitoring"""
        try:
            # Record request count
            key = f"{method}:{endpoint}"
            if key not in self.request_counts:
                self.request_counts[key] = {'total': 0, 'success': 0, 'error': 0}
            
            self.request_counts[key]['total'] += 1
            
            if 200 <= status_code < 400:
                self.request_counts[key]['success'] += 1
            else:
                self.request_counts[key]['error'] += 1
            
            # Record response time
            self.response_times.append(response_time)
            if len(self.response_times) > self.max_response_times:
                self.response_times.pop(0)
            
            # Log slow requests
            if response_time > self.slow_request_threshold:
                logger.warning(f"Slow request detected: {method} {endpoint} took {response_time:.2f}s")
            
            # Record errors
            if status_code >= 400:
                error_key = f"{method}:{endpoint}:{status_code}"
                self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
                
        except Exception as e:
            logger.error(f"Error recording request: {e}")
    
    def _check_system_health(self):
        """Check system health and log warnings"""
        try:
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                logger.warning(f"High memory usage: {memory.percent:.1f}%")
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                logger.warning(f"High disk usage: {disk.percent:.1f}%")
            
            # Check error rates
            self._check_error_rates()
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
    
    def _check_error_rates(self):
        """Check error rates and log warnings"""
        try:
            for endpoint, counts in self.request_counts.items():
                if counts['total'] > 10:  # Only check if we have enough data
                    error_rate = counts['error'] / counts['total']
                    if error_rate > self.error_rate_threshold:
                        logger.warning(f"High error rate for {endpoint}: {error_rate:.1%}")
        except Exception as e:
            logger.error(f"Error rate check failed: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current application metrics"""
        try:
            # System metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            disk = psutil.disk_usage('/')
            
            # Application metrics
            uptime = time.time() - self.start_time
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            # Cache metrics
            cache_stats = get_cache_stats()
            
            # Rate limiting info (if available)
            rate_limit_stats = self._get_rate_limit_stats()
            
            return {
                'system': {
                    'memory_percent': memory.percent,
                    'cpu_percent': cpu_percent,
                    'disk_percent': disk.percent,
                    'uptime_seconds': uptime,
                    'uptime_human': str(timedelta(seconds=int(uptime)))
                },
                'application': {
                    'total_requests': sum(counts['total'] for counts in self.request_counts.values()),
                    'total_errors': sum(counts['error'] for counts in self.request_counts.values()),
                    'avg_response_time': round(avg_response_time, 3),
                    'slow_requests': len([rt for rt in self.response_times if rt > self.slow_request_threshold]),
                    'endpoints': self.request_counts
                },
                'cache': cache_stats,
                'rate_limiting': rate_limit_stats,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        try:
            import redis
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=1,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1
            )
            
            # Get all rate limit keys
            keys = redis_client.keys('rate_limit:*')
            total_rate_limited_ips = len(keys)
            
            # Get total rate limit hits
            total_hits = 0
            for key in keys:
                total_hits += redis_client.zcard(key)
            
            return {
                'total_rate_limited_ips': total_rate_limited_ips,
                'total_rate_limit_hits': total_hits,
                'storage_type': 'redis'
            }
            
        except Exception as e:
            logger.warning(f"Failed to get rate limit stats: {e}")
            return {
                'storage_type': 'memory',
                'error': str(e)
            }

# Global monitor instance
app_monitor = ApplicationMonitor()

def monitor_request(f):
    """Decorator to monitor request performance"""
    def decorator(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Extract request info (this is a simplified version)
            # In a real implementation, you'd get this from Flask request context
            app_monitor.record_request(
                endpoint=f.__name__,
                method='GET',  # Simplified
                status_code=200,
                response_time=response_time
            )
            
            return result
        except Exception as e:
            response_time = time.time() - start_time
            app_monitor.record_request(
                endpoint=f.__name__,
                method='GET',  # Simplified
                status_code=500,
                response_time=response_time
            )
            raise
    return decorator 