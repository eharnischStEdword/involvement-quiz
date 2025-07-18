# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import logging
import logging.handlers
import os
import sys
from datetime import datetime

def setup_logging(level='INFO', log_file=None):
    """
    Set up structured logging with proper formatting and handlers
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging to file
    """
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create handlers list
    handlers = [console_handler]
    
    # Add file handler if log_file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create rotating file handler (10MB max, keep 5 files)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, level.upper()))
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set specific logger levels
    loggers = {
        'werkzeug': 'WARNING',  # Reduce Flask development server noise
        'urllib3': 'WARNING',   # Reduce HTTP request noise
        'requests': 'WARNING',  # Reduce HTTP request noise
        'app': 'DEBUG',         # Full debug for our app
    }
    
    for logger_name, logger_level in loggers.items():
        logging.getLogger(logger_name).setLevel(getattr(logging, logger_level.upper()))

def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)

def log_request_info(request, logger=None):
    """Log request information for debugging"""
    if logger is None:
        logger = get_logger('app.requests')
    
    logger.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")

def log_database_operation(operation, table, logger=None):
    """Log database operations for monitoring"""
    if logger is None:
        logger = get_logger('app.database')
    
    logger.info(f"Database operation: {operation} on table {table}")

def log_performance_metric(metric_name, value, unit=None, logger=None):
    """Log performance metrics"""
    if logger is None:
        logger = get_logger('app.performance')
    
    unit_str = f" {unit}" if unit else ""
    logger.info(f"Performance metric: {metric_name} = {value}{unit_str}")

def log_security_event(event_type, details, logger=None):
    """Log security-related events"""
    if logger is None:
        logger = get_logger('app.security')
    
    logger.warning(f"Security event: {event_type} - {details}")

def log_user_action(user_id, action, details=None, logger=None):
    """Log user actions for audit trail"""
    if logger is None:
        logger = get_logger('app.user_actions')
    
    details_str = f" - {details}" if details else ""
    logger.info(f"User action: {user_id} - {action}{details_str}")

def log_error_with_context(error, context=None, logger=None):
    """Log errors with additional context"""
    if logger is None:
        logger = get_logger('app.errors')
    
    context_str = f" - Context: {context}" if context else ""
    logger.error(f"Error: {str(error)}{context_str}", exc_info=True) 