# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

from flask import Blueprint, request, jsonify
import json
import logging
import psycopg2.extras
from datetime import datetime

from app.database import get_db_connection
from app.utils import check_rate_limit
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
                validated_data['age_group'],
                validated_data['gender'],
                json.dumps(validated_data['states']),
                json.dumps(validated_data['interests']),
                json.dumps(validated_data['situation']),
                json.dumps(validated_data['ministries']),
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
