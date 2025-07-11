# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import os
import time
import hashlib
import logging
from functools import wraps
from flask import request, session, jsonify
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)

# Login attempt tracking
login_attempts = defaultdict(list)
attempts_lock = Lock()

# Configuration
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW = 900  # 15 minutes in seconds
LOCKOUT_DURATION = 3600  # 1 hour in seconds

# Admin credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'stedward_admin')
ADMIN_PASSWORD_HASH = hashlib.sha256(
    os.environ.get('ADMIN_PASSWORD', 'change_this_password_123!').encode()
).hexdigest()

def check_login_rate_limit(ip_address):
    """Check if IP is allowed to attempt login"""
    current_time = time.time()
    
    with attempts_lock:
        # Clean old attempts
        login_attempts[ip_address] = [
            timestamp for timestamp in login_attempts[ip_address]
            if current_time - timestamp < LOGIN_WINDOW
        ]
        
        # Check if locked out
        if len(login_attempts[ip_address]) >= MAX_LOGIN_ATTEMPTS:
            oldest_attempt = min(login_attempts[ip_address])
            if current_time - oldest_attempt < LOCKOUT_DURATION:
                return False, int((oldest_attempt + LOCKOUT_DURATION) - current_time)
        
        return True, 0

def record_login_attempt(ip_address):
    """Record a failed login attempt"""
    with attempts_lock:
        login_attempts[ip_address].append(time.time())

def clear_login_attempts(ip_address):
    """Clear login attempts after successful login"""
    with attempts_lock:
        if ip_address in login_attempts:
            del login_attempts[ip_address]

def require_admin_auth_enhanced(f):
    """Enhanced admin authentication with rate limiting and session support"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Check if already authenticated via session
        if session.get('admin_authenticated'):
            # Verify session hasn't expired (24 hour timeout)
            if time.time() - session.get('auth_time', 0) > 86400:
                session.clear()
            else:
                return f(*args, **kwargs)
        
        # Check rate limiting
        allowed, lockout_remaining = check_login_rate_limit(ip_address)
        if not allowed:
            return jsonify({
                'error': 'Too many login attempts',
                'lockout_remaining_seconds': lockout_remaining
            }), 429
        
        # Check basic auth
        auth = request.authorization
        if not auth:
            return ('Admin authentication required', 401, {
                'WWW-Authenticate': 'Basic realm="St. Edward Admin"'
            })
        
        # Verify credentials
        password_hash = hashlib.sha256(auth.password.encode()).hexdigest()
        if auth.username != ADMIN_USERNAME or password_hash != ADMIN_PASSWORD_HASH:
            record_login_attempt(ip_address)
            logger.warning(f"Failed admin login attempt from {ip_address}")
            return ('Invalid credentials', 401, {
                'WWW-Authenticate': 'Basic realm="St. Edward Admin"'
            })
        
        # Successful login
        clear_login_attempts(ip_address)
        session['admin_authenticated'] = True
        session['auth_time'] = time.time()
        session['admin_ip'] = ip_address
        
        return f(*args, **kwargs)
    
    return decorated_function

# CSRF token management
def generate_csrf_token():
    """Generate a CSRF token for the session"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = hashlib.sha256(os.urandom(32)).hexdigest()
    return session['_csrf_token']

def validate_csrf_token():
    """Validate CSRF token from request"""
    token = request.form.get('_csrf_token') or \
            request.headers.get('X-CSRF-Token') or \
            request.json.get('_csrf_token') if request.is_json else None
    
    return token == session.get('_csrf_token')

def require_csrf_token(f):
    """Decorator to require CSRF token for state-changing operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            if not validate_csrf_token():
                return jsonify({'error': 'Invalid CSRF token'}), 403
        return f(*args, **kwargs)
    
    return decorated_function
