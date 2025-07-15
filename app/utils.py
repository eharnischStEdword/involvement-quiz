# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import os
import time
from functools import wraps
from flask import request
import logging

logger = logging.getLogger(__name__)

# Simple rate limiting storage (in production, use Redis)
request_counts = {}
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
    """Simple rate limiting - max 5 submissions per hour per IP"""
    current_time = time.time()
    
    # Clean old entries
    cutoff_time = current_time - RATE_LIMIT_WINDOW
    request_counts.update({ip: [t for t in times if t > cutoff_time] 
                          for ip, times in request_counts.items()})
    
    # Check current IP
    if ip_address not in request_counts:
        request_counts[ip_address] = []
    
    request_counts[ip_address] = [t for t in request_counts[ip_address] if t > cutoff_time]
    
    if len(request_counts[ip_address]) >= RATE_LIMIT_REQUESTS:
        return False
    
    request_counts[ip_address].append(current_time)
    return True

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
