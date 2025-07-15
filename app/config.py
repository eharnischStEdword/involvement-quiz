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
        
        logger.info(f"Environment validation passed for {env} mode")
        return env
    
    @classmethod
    def get_config(cls):
        """Get configuration based on environment"""
        env = cls.validate_environment()
        
        return {
            'SECRET_KEY': os.environ.get('SECRET_KEY'),
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'ADMIN_USERNAME': os.environ.get('ADMIN_USERNAME'),
            'ADMIN_PASSWORD': os.environ.get('ADMIN_PASSWORD'),
            'DEBUG': env == 'development',  # Only debug in development
            'FLASK_ENV': env,
            'IS_PRODUCTION': env == 'production'
        }
