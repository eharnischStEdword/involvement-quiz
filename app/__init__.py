# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman
from flask_caching import Cache
import logging

from app.config import Config
from app.models import init_db
from app.database import init_connection_pool, close_connection_pool
from app.logging_config import setup_logging, get_logger
from app.migrations import run_migrations

def create_app(config=None):
    """Application factory pattern for better testing and configuration"""
    
    # Validate environment and get configuration
    if config is None:
        config = Config.get_config()
    
    app = Flask(__name__, template_folder='../templates')
    CORS(app)
    app.secret_key = config['SECRET_KEY']
    
    # Configure Talisman for HTTPS with proper CSP settings
    if config['IS_PRODUCTION']:
        csp = {
            'default-src': "'self'",
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Required for event handlers
                "'unsafe-eval'",    # Required for Chart.js
                'https://cdn.jsdelivr.net',
                'https://cdnjs.cloudflare.com',
                'https://www.googletagmanager.com',
                'https://www.google-analytics.com'
            ],
            'worker-src': ["'self'"],  # Allow service workers
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Required for style attributes
                'https://cdnjs.cloudflare.com',
                'https://fonts.googleapis.com'
            ],
            'font-src': [
                "'self'",
                'https://cdnjs.cloudflare.com',
                'https://fonts.gstatic.com'
            ],
            'img-src': [
                "'self'",
                'data:',
                'https:',
                'http:'
            ],
            'connect-src': [
                "'self'",
                'https://www.google-analytics.com'
            ]
        }
        Talisman(app, 
                 force_https=True, 
                 strict_transport_security=True,
                 content_security_policy=csp)
    
    # Configure caching
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    
    # Set up enhanced logging
    log_level = 'DEBUG' if config.get('DEBUG', False) else 'INFO'
    setup_logging(level=log_level)
    logger = get_logger(__name__)
    
    # Initialize database and connection pool
    try:
        init_db()
        init_connection_pool()
        logger.info("Database and connection pool initialized")
        
        # Run database migrations
        run_migrations()
        logger.info("Database migrations completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Register blueprints
    from app.blueprints.public import public_bp
    from app.blueprints.api import api_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.ministry_admin import ministry_admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ministry_admin_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    # Teardown context
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        # Connection pool handles cleanup automatically
        pass
    
    return app


