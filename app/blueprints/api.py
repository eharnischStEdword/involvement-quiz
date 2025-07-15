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
            return jsonify({
                'success': False,
                'message': 'Too many submissions from this location. Please try again in an hour.'
            }), 429
        
        data = request.json
        logger.info(f"Received submission from IP {ip_address}: {data}")
        
        with get_db_connection() as (conn, cur):
            name = "Anonymous User"
            email = ""
            answers = data.get('answers', {})
            ministries = data.get('ministries', [])
            situation = data.get('situation', [])
            states = data.get('states', [])
            interests = data.get('interests', [])
            
            cur.execute('''
                INSERT INTO ministry_submissions 
                (name, email, age_group, gender, state_in_life, interest, situation, recommended_ministries, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                name, email,
                answers.get('age', ''),
                answers.get('gender', ''),
                json.dumps(states),
                json.dumps(interests),
                json.dumps(situation),
                json.dumps(ministries),
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
        logger.error(f"Database error in submit_ministry_interest: {e}")
        return jsonify({
            'success': False,
            'message': 'Database connection issue. Please try again or contact the parish office at (615) 833-5520.'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in submit_ministry_interest: {e}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again or contact the parish office.'
        }), 500

@api_bp.route('/submit-contact', methods=['POST'])
def submit_contact():
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        if not check_rate_limit(ip_address):
            logger.warning(f"Rate limit exceeded for contact form from IP: {ip_address}")
            return jsonify({
                'success': False,
                'message': 'Too many submissions from this location. Please try again in an hour.'
            }), 429
        
        data = request.json
        logger.info(f"Received contact form from IP {ip_address}: {data.get('name', 'Unknown')}")
        
        with get_db_connection() as (conn, cur):
            cur.execute('''
                CREATE TABLE IF NOT EXISTS contact_submissions (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(20),
                    message TEXT,
                    quiz_results JSONB,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45),
                    contacted BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cur.execute('''
                INSERT INTO contact_submissions 
                (name, email, phone, message, quiz_results, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                data.get('name', ''),
                data.get('email', ''),
                data.get('phone', ''),
                data.get('message', ''),
                json.dumps(data.get('quiz_results', {})),
                ip_address
            ))
            
            contact_id = cur.fetchone()[0]
        
        logger.info(f"Successfully saved contact submission {contact_id} from {data.get('name', 'Unknown')}")
        
        return jsonify({
            'success': True,
            'message': 'Contact information received successfully!',
            'contact_id': contact_id
        })
        
    except psycopg2.Error as e:
        logger.error(f"Database error in submit_contact: {e}")
        return jsonify({
            'success': False,
            'message': 'Database error. Please try again or call (615) 833-5520.'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in submit_contact: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again or call (615) 833-5520.'
        }), 500

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
