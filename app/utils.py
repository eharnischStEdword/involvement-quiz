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

# Rate limiting configuration - Set very high to allow multiple quiz attempts
RATE_LIMIT_REQUESTS = 1000  # Very high limit to allow multiple attempts
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# New configuration for engagement tracking
ENABLE_RATE_LIMITING = False  # Allow multiple quiz attempts
TRACK_ENGAGEMENT = True  # Track user engagement patterns

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
    """Rate limiting - currently disabled to allow multiple quiz attempts"""
    if not ENABLE_RATE_LIMITING:
        return True  # Allow all submissions
    # Use in-memory rate limiting for simplicity
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
        # Use in-memory rate limiting info
        current_time = time.time()
        
        # Get current requests from memory
        if not hasattr(_check_rate_limit_memory, 'request_counts'):
            _check_rate_limit_memory.request_counts = {}
        
        if ip_address not in _check_rate_limit_memory.request_counts:
            _check_rate_limit_memory.request_counts[ip_address] = []
        
        # Clean old entries
        cutoff_time = current_time - RATE_LIMIT_WINDOW
        _check_rate_limit_memory.request_counts[ip_address] = [
            t for t in _check_rate_limit_memory.request_counts[ip_address] 
            if t > cutoff_time
        ]
        
        remaining_requests = max(0, RATE_LIMIT_REQUESTS - len(_check_rate_limit_memory.request_counts[ip_address]))
        
        return {
            'remaining_requests': remaining_requests,
            'limit': RATE_LIMIT_REQUESTS,
            'window_seconds': RATE_LIMIT_WINDOW,
            'reset_time': current_time + RATE_LIMIT_WINDOW,
            'storage_type': 'memory'
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
