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

from app.config import Config

logger = logging.getLogger(__name__)

# Login attempt tracking
login_attempts = defaultdict(list)
attempts_lock = Lock()

# Configuration
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW = 900  # 15 minutes in seconds
LOCKOUT_DURATION = 3600  # 1 hour in seconds
MAX_TRACKED_IPS = 1000  # Maximum number of IPs to track
CLEANUP_INTERVAL = 3600  # Cleanup every hour
last_cleanup = time.time()

def cleanup_old_attempts():
    """Clean up old login attempts to prevent memory leaks"""
    global last_cleanup, login_attempts
    
    current_time = time.time()
    if current_time - last_cleanup < CLEANUP_INTERVAL:
        return
    
    with attempts_lock:
        # Remove old attempts from all IPs
        for ip_address in list(login_attempts.keys()):
            login_attempts[ip_address] = [
                timestamp for timestamp in login_attempts[ip_address]
                if current_time - timestamp < LOGIN_WINDOW
            ]
            
            # Remove IP if no attempts remain
            if not login_attempts[ip_address]:
                del login_attempts[ip_address]
        
        # Limit number of tracked IPs
        if len(login_attempts) > MAX_TRACKED_IPS:
            # Remove oldest IPs (simple FIFO)
            oldest_ips = list(login_attempts.keys())[:len(login_attempts) - MAX_TRACKED_IPS]
            for ip in oldest_ips:
                del login_attempts[ip]
            logger.debug(f"Cleaned up {len(oldest_ips)} old IPs from login tracking")
        
        last_cleanup = current_time

def check_login_rate_limit(ip_address):
    """Check if IP is allowed to attempt login"""
    current_time = time.time()
    
    # Periodic cleanup
    cleanup_old_attempts()
    
    with attempts_lock:
        # Clean old attempts for this IP
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
    current_time = time.time()
    
    with attempts_lock:
        login_attempts[ip_address].append(current_time)
        
        # Keep only recent attempts within the window
        login_attempts[ip_address] = [
            timestamp for timestamp in login_attempts[ip_address]
            if current_time - timestamp < LOGIN_WINDOW
        ]

def clear_login_attempts(ip_address):
    """Clear login attempts for an IP (successful login)"""
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
            # Verify session hasn't expired using configurable timeout
            config = Config.get_config()
            if config:
                session_timeout = config.get('SESSION_TIMEOUT', 3600)  # Default 1 hour
            else:
                session_timeout = 3600  # Fallback default
            
            if time.time() - session.get('auth_time', 0) > session_timeout:
                session.clear()
                logger.info(f"Admin session expired for IP {ip_address}")
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
        if not auth.password:
            record_login_attempt(ip_address)
            logger.warning(f"Failed admin login attempt from {ip_address} - no password")
            return ('Invalid credentials', 401, {
                'WWW-Authenticate': 'Basic realm="St. Edward Admin"'
            })
        
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
        
        logger.info(f"Successful admin login from IP {ip_address}")
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

# Admin credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'stedward_admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change_this_password_123!')
if ADMIN_PASSWORD:
    ADMIN_PASSWORD_HASH = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
else:
    ADMIN_PASSWORD_HASH = ''
