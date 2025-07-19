# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

from flask import Blueprint, request, jsonify
import json
import logging
import psycopg2.extras
from datetime import datetime

from app.database import get_db_connection
from app.utils import check_rate_limit, get_rate_limit_info
from app.monitoring import app_monitor
from app.validators import validate_and_respond
from app.error_handlers import create_error_response, RateLimitError, DatabaseError, ValidationError

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api_bp.route('/submit', methods=['POST'])
def submit_ministry_interest():
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        if not check_rate_limit(ip_address):
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            error_response, status_code = create_error_response(RateLimitError())
            return jsonify(error_response), status_code
        
        data = request.json
        if not data:
            error_response, status_code = create_error_response(ValidationError("No data provided"))
            return jsonify(error_response), status_code
        
        logger.info(f"Received submission from IP {ip_address}: {data}")
        
        # Validate input data
        validated_data, error_response = validate_and_respond(data)
        if error_response:
            return error_response
        
        # Ensure validated_data is not None
        if not validated_data:
            error_response, status_code = create_error_response(ValidationError("Validation failed"))
            return jsonify(error_response), status_code
        
        with get_db_connection() as (conn, cur):
            name = "Anonymous User"
            email = ""
            
            cur.execute('''
                INSERT INTO ministry_submissions 
                (name, email, age_group, gender, state_in_life, interest, situation, recommended_ministries, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                name, email,
                validated_data.get('age_group', ''),
                validated_data.get('gender', ''),
                json.dumps(validated_data.get('states', [])),
                json.dumps(validated_data.get('interests', [])),
                json.dumps(validated_data.get('situation', [])),
                json.dumps(validated_data.get('ministries', [])),
                ip_address
            ))
            
            submission_id = cur.fetchone()[0]
        
        logger.info(f"Successfully saved anonymous submission {submission_id} from IP {ip_address}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for exploring St. Edward ministries!',
            'submission_id': submission_id
        })
        
    except psycopg2.Error as e:
        error_response, status_code = create_error_response(DatabaseError("Database operation failed", e))
        return jsonify(error_response), status_code
        
    except Exception as e:
        error_response, status_code = create_error_response(e)
        return jsonify(error_response), status_code



@api_bp.route('/health')
def health_check():
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/rate-limit-info')
def rate_limit_info():
    """Get rate limit information for the current IP"""
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        rate_info = get_rate_limit_info(ip_address)
        
        return jsonify({
            'ip_address': ip_address,
            'rate_limit': rate_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Rate limit info failed: {e}")
        return jsonify({
            'error': 'Failed to get rate limit information',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/metrics')
def get_metrics():
    """Get application performance metrics"""
    try:
        metrics = app_monitor.get_metrics()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return jsonify({
            'error': 'Failed to get metrics',
            'timestamp': datetime.now().isoformat()
        }), 500
# --- TEMPORARY DEBUG ENDPOINT ----------------------------------------------
@api_bp.route('/debug/mass')
def debug_mass():
    """
    Quick check that the Mass ministry row exists and is active.
    Visit /api/debug/mass in the browser.
    Remove this route once you’re satisfied.
    """
    try:
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            cur.execute("SELECT * FROM ministries WHERE ministry_key = 'mass'")
            row = cur.fetchone()
        return jsonify({
            'found': bool(row),
            'active': row['active'] if row else None,
            'row': row
        })
    except Exception as e:
        logger.error(f'/debug/mass failed: {e}')
        return jsonify({'error': str(e)}), 500

@api_bp.route('/debug/submissions')
def debug_submissions():
    """
    Debug endpoint to check recent submissions and database status.
    Visit /api/debug/submissions in the browser.
    """
    try:
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            # Check table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'ministry_submissions' 
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            
            # Check recent submissions
            cur.execute("""
                SELECT id, submitted_at, age_group, gender 
                FROM ministry_submissions 
                ORDER BY submitted_at DESC 
                LIMIT 5
            """)
            recent = cur.fetchall()
            
            # Count total submissions
            cur.execute("SELECT COUNT(*) as total FROM ministry_submissions")
            total = cur.fetchone()
            
        return jsonify({
            'table_structure': [dict(col) for col in columns],
            'recent_submissions': [dict(sub) for sub in recent],
            'total_submissions': total['total'] if total else 0,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f'/debug/submissions failed: {e}')
        return jsonify({'error': str(e)}), 500

@api_bp.route('/memory-status')
def memory_status():
    """Get current memory status for monitoring"""
    try:
        import psutil
        
        # Get process memory info
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # Get system memory info
        system_memory = psutil.virtual_memory()
        
        # Get cache stats
        from app.cache import get_cache_stats
        cache_stats = get_cache_stats()
        
        # Get monitoring metrics
        from app.monitoring import app_monitor
        monitoring_metrics = app_monitor.get_metrics()
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'process': {
                'rss_mb': round(memory_info.rss / (1024 * 1024), 2),
                'vms_mb': round(memory_info.vms / (1024 * 1024), 2),
                'percent': round(memory_percent, 2)
            },
            'system': {
                'total_gb': round(system_memory.total / (1024 * 1024 * 1024), 2),
                'available_gb': round(system_memory.available / (1024 * 1024 * 1024), 2),
                'percent': round(system_memory.percent, 2)
            },
            'cache': cache_stats,
            'monitoring': monitoring_metrics.get('application', {}).get('monitoring_data_size', {})
        })
        
    except ImportError:
        return jsonify({
            'error': 'psutil not available',
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error(f"Memory status check failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
