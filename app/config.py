# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import os
import sys
import logging

logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration with validation"""
    
    # Required environment variables
    REQUIRED_ENV_VARS = {
        'production': [
            'DATABASE_URL',
            'SECRET_KEY',
            'ADMIN_USERNAME', 
            'ADMIN_PASSWORD'
        ],
        'development': []
    }
    
    # Security defaults
    DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour in seconds
    MAX_SESSION_TIMEOUT = 86400     # 24 hours maximum
    MIN_SESSION_TIMEOUT = 900       # 15 minutes minimum
    
    @classmethod
    def validate_environment(cls):
        """Validate required environment variables are set"""
        env = 'production' if os.environ.get('DATABASE_URL') else 'development'
        missing_vars = []
        
        for var in cls.REQUIRED_ENV_VARS.get(env, []):
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please set these variables before starting the application.")
            sys.exit(1)
        
        # Validate no defaults are being used in production
        if env == 'production':
            if os.environ.get('SECRET_KEY') == 'your-secret-key-here-change-in-production':
                logger.error("SECURITY ERROR: Using default SECRET_KEY in production!")
                sys.exit(1)
            
            if os.environ.get('ADMIN_PASSWORD') == 'change_this_password_123!':
                logger.error("SECURITY ERROR: Using default ADMIN_PASSWORD in production!")
                sys.exit(1)
            
            # Validate SECRET_KEY strength
            secret_key = os.environ.get('SECRET_KEY', '')
            if len(secret_key) < 32:
                logger.error("SECURITY ERROR: SECRET_KEY must be at least 32 characters long!")
                sys.exit(1)
            
            # Validate ADMIN_PASSWORD strength
            admin_password = os.environ.get('ADMIN_PASSWORD', '')
            if len(admin_password) < 8:
                logger.error("SECURITY ERROR: ADMIN_PASSWORD must be at least 8 characters long!")
                sys.exit(1)
        
        logger.info(f"Environment validation passed for {env} mode")
        return env
    
    @classmethod
    def get_session_timeout(cls):
        """Get configured session timeout with validation"""
        try:
            timeout = int(os.environ.get('SESSION_TIMEOUT', cls.DEFAULT_SESSION_TIMEOUT))
            
            if timeout < cls.MIN_SESSION_TIMEOUT:
                logger.warning(f"Session timeout {timeout}s is too short, using minimum {cls.MIN_SESSION_TIMEOUT}s")
                timeout = cls.MIN_SESSION_TIMEOUT
            elif timeout > cls.MAX_SESSION_TIMEOUT:
                logger.warning(f"Session timeout {timeout}s is too long, using maximum {cls.MAX_SESSION_TIMEOUT}s")
                timeout = cls.MAX_SESSION_TIMEOUT
            
            return timeout
        except ValueError:
            logger.warning(f"Invalid SESSION_TIMEOUT value, using default {cls.DEFAULT_SESSION_TIMEOUT}s")
            return cls.DEFAULT_SESSION_TIMEOUT
    
    @classmethod
    def get_config(cls):
        """Get configuration based on environment"""
        env = cls.validate_environment()
        
        return {
            'SECRET_KEY': os.environ.get('SECRET_KEY'),
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'ADMIN_USERNAME': os.environ.get('ADMIN_USERNAME'),
            'ADMIN_PASSWORD': os.environ.get('ADMIN_PASSWORD'),
            'SESSION_TIMEOUT': cls.get_session_timeout(),
            'DEBUG': env == 'development',  # Only debug in development
            'FLASK_ENV': env,
            'IS_PRODUCTION': env == 'production'
        }
