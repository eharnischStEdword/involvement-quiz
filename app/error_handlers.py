# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import logging
import traceback
from typing import Dict, Any, Optional, Tuple
from flask import jsonify, current_app
import psycopg2
import psycopg2.pool

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error class"""
    def __init__(self, message: str, status_code: int = 500, user_message: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.user_message = user_message or "An unexpected error occurred. Please try again."
        super().__init__(self.message)

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, 400, f"Invalid data: {message}")
        self.field = field

class DatabaseError(AppError):
    """Database error"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        user_msg = "Database connection issue. Please try again or contact the parish office."
        super().__init__(message, 500, user_msg)
        self.original_error = original_error

class RateLimitError(AppError):
    """Rate limit error"""
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, 429, "Too many submissions from this location. Please try again in an hour.")

class ServiceUnavailableError(AppError):
    """Service unavailable error"""
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, 503, "Service temporarily unavailable. Please try again later.")

def handle_database_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle database-related errors gracefully"""
    logger.error(f"Database error: {error}")
    
    # Log the full traceback for debugging
    logger.error(f"Database error traceback: {traceback.format_exc()}")
    
    if isinstance(error, psycopg2.OperationalError):
        # Connection issues
        return {
            'success': False,
            'message': 'Database connection issue. Please try again or contact the parish office at (615) 833-5520.',
            'error_type': 'database_connection'
        }, 500
    
    elif isinstance(error, psycopg2.IntegrityError):
        # Data integrity issues
        return {
            'success': False,
            'message': 'Data integrity error. Please check your input and try again.',
            'error_type': 'data_integrity'
        }, 400
    
    elif isinstance(error, psycopg2.pool.PoolError):
        # Connection pool issues
        return {
            'success': False,
            'message': 'Service temporarily unavailable. Please try again in a moment.',
            'error_type': 'connection_pool'
        }, 503
    
    else:
        # Generic database error
        return {
            'success': False,
            'message': 'Database error occurred. Please try again or contact support.',
            'error_type': 'database_error'
        }, 500

def handle_validation_error(error: ValidationError) -> Tuple[Dict[str, Any], int]:
    """Handle validation errors"""
    logger.warning(f"Validation error: {error.message}")
    
    return {
        'success': False,
        'message': 'Validation failed',
        'errors': [error.message],
        'field': error.field,
        'error_type': 'validation_error'
    }, 400

def handle_rate_limit_error(error: RateLimitError) -> Tuple[Dict[str, Any], int]:
    """Handle rate limit errors"""
    logger.warning(f"Rate limit exceeded: {error.message}")
    
    return {
        'success': False,
        'message': error.user_message,
        'error_type': 'rate_limit'
    }, 429

def handle_generic_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle generic errors"""
    logger.error(f"Unexpected error: {error}")
    logger.error(f"Error traceback: {traceback.format_exc()}")
    
    # In production, don't expose internal error details
    if current_app.config.get('DEBUG', False):
        return {
            'success': False,
            'message': f'Unexpected error: {str(error)}',
            'error_type': 'unexpected_error'
        }, 500
    else:
        return {
            'success': False,
            'message': 'An unexpected error occurred. Please try again or contact the parish office.',
            'error_type': 'unexpected_error'
        }, 500

def create_error_response(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Create appropriate error response based on error type"""
    
    if isinstance(error, ValidationError):
        return handle_validation_error(error)
    
    elif isinstance(error, DatabaseError):
        return handle_database_error(error.original_error or error)
    
    elif isinstance(error, RateLimitError):
        return handle_rate_limit_error(error)
    
    elif isinstance(error, ServiceUnavailableError):
        return {
            'success': False,
            'message': error.user_message,
            'error_type': 'service_unavailable'
        }, error.status_code
    
    elif isinstance(error, psycopg2.Error):
        return handle_database_error(error)
    
    else:
        return handle_generic_error(error)

def safe_database_operation(operation_func, *args, **kwargs):
    """
    Safely execute database operations with error handling
    
    Usage:
        result = safe_database_operation(
            lambda: execute_query("SELECT * FROM table"),
            fallback_value=[]
        )
    """
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        error_response, status_code = create_error_response(e)
        raise AppError(
            error_response['message'], 
            status_code, 
            error_response['message']
        )

def retry_operation(operation_func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry an operation with exponential backoff
    
    Usage:
        result = retry_operation(
            lambda: database_operation(),
            max_retries=3,
            delay=1.0
        )
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return operation_func()
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, raise the error
                raise
            
            # Log the retry attempt
            logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            # Wait before retrying (exponential backoff)
            wait_time = delay * (2 ** attempt)
            time.sleep(wait_time)
    
    # This should never be reached, but just in case
    raise Exception("Operation failed after all retry attempts")

def log_error_with_context(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log error with additional context for debugging"""
    error_info: Dict[str, Any] = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc()
    }
    
    if context:
        error_info['context'] = context
    
    logger.error(f"Error with context: {error_info}")
    
    return error_info 