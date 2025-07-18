# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import os
import time
from functools import wraps
from flask import request
import logging

from app.logging_config import get_logger

logger = get_logger(__name__)

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 5  # Max 5 submissions per hour per IP
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Admin credentials from environment - NO DEFAULTS IN PRODUCTION
def get_admin_credentials():
    """Get admin credentials from environment variables"""
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    
    if not username or not password:
        logger.error("Admin credentials not properly configured")
        raise ValueError("Admin credentials must be set via environment variables")
    
    return username, password

def check_rate_limit(ip_address):
    """Redis-based rate limiting - max 5 submissions per hour per IP"""
    try:
        import redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=1,  # Use different DB for rate limiting
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1
        )
        
        # Test Redis connection
        redis_client.ping()
        
        # Use Redis for rate limiting
        current_time = time.time()
        key = f"rate_limit:{ip_address}"
        
        # Get current requests for this IP
        requests = redis_client.zrangebyscore(key, current_time - RATE_LIMIT_WINDOW, '+inf')
        
        if len(requests) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return False
        
        # Add current request
        redis_client.zadd(key, {str(current_time): current_time})
        redis_client.expire(key, RATE_LIMIT_WINDOW)
        
        logger.debug(f"Rate limit check passed for IP: {ip_address}")
        return True
        
    except ImportError:
        logger.warning("Redis package not installed, falling back to in-memory rate limiting")
        return _check_rate_limit_memory(ip_address)
    except Exception as e:
        logger.warning(f"Redis rate limiting failed, falling back to in-memory: {e}")
        return _check_rate_limit_memory(ip_address)

def _check_rate_limit_memory(ip_address):
    """Fallback in-memory rate limiting"""
    # Simple rate limiting storage (fallback)
    if not hasattr(_check_rate_limit_memory, 'request_counts'):
        _check_rate_limit_memory.request_counts = {}
    
    current_time = time.time()
    
    # Clean old entries
    cutoff_time = current_time - RATE_LIMIT_WINDOW
    _check_rate_limit_memory.request_counts.update({ip: [t for t in times if t > cutoff_time] 
                          for ip, times in _check_rate_limit_memory.request_counts.items()})
    
    # Check current IP
    if ip_address not in _check_rate_limit_memory.request_counts:
        _check_rate_limit_memory.request_counts[ip_address] = []
    
    _check_rate_limit_memory.request_counts[ip_address] = [t for t in _check_rate_limit_memory.request_counts[ip_address] if t > cutoff_time]
    
    if len(_check_rate_limit_memory.request_counts[ip_address]) >= RATE_LIMIT_REQUESTS:
        return False
    
    _check_rate_limit_memory.request_counts[ip_address].append(current_time)
    return True

def get_rate_limit_info(ip_address):
    """Get rate limit information for an IP address"""
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
        
        redis_client.ping()
        current_time = time.time()
        key = f"rate_limit:{ip_address}"
        
        # Get current requests
        requests = redis_client.zrangebyscore(key, current_time - RATE_LIMIT_WINDOW, '+inf')
        remaining_requests = max(0, RATE_LIMIT_REQUESTS - len(requests))
        
        # Get TTL for the key
        ttl = redis_client.ttl(key)
        
        return {
            'remaining_requests': remaining_requests,
            'limit': RATE_LIMIT_REQUESTS,
            'window_seconds': RATE_LIMIT_WINDOW,
            'reset_time': current_time + ttl if ttl > 0 else current_time + RATE_LIMIT_WINDOW,
            'storage_type': 'redis'
        }
        
    except Exception as e:
        logger.warning(f"Failed to get rate limit info: {e}")
        return {
            'remaining_requests': 'unknown',
            'limit': RATE_LIMIT_REQUESTS,
            'window_seconds': RATE_LIMIT_WINDOW,
            'storage_type': 'memory'
        }

def require_admin_auth(f):
    """Decorator for admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        
        try:
            admin_username, admin_password = get_admin_credentials()
        except ValueError:
            return ('Configuration error', 500)
        
        if not auth or auth.username != admin_username or auth.password != admin_password:
            return ('Admin authentication required', 401, {
                'WWW-Authenticate': 'Basic realm="St. Edward Admin"'
            })
        return f(*args, **kwargs)
    return decorated_function
