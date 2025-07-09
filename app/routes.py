from flask import request, jsonify, render_template
from functools import wraps
import json
import logging
import psycopg2.extras
from datetime import datetime

from app.database import get_db_connection, execute_query
from app.ministries import MINISTRY_DATA
from app.utils import check_rate_limit
from app.auth import require_admin_auth_enhanced as require_admin_auth, require_csrf_token, generate_csrf_token

logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/')
    def index():
        """Serve the template with proper Flask template rendering"""
        return render_template('index.html')

    @app.route('/api/submit', methods=['POST'])
    def submit_ministry_interest():
        try:
            # Get client IP address
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            if ',' in ip_address:  # Handle multiple IPs in forwarded header
                ip_address = ip_address.split(',')[0].strip()
            
            # Check rate limit
            if not check_rate_limit(ip_address):
                logger.warning(f"Rate limit exceeded for IP: {ip_address}")
                return jsonify({
                    'success': False,
                    'message': 'Too many submissions from this location. Please try again in an hour.'
                }), 429
            
            data = request.json
            logger.info(f"Received submission from IP {ip_address}: {data}")
            
            # For anonymous tracking, we don't require email
            email = ""  # Store empty string for anonymous submissions
            
            with get_db_connection() as (conn, cur):
                # Extract data with defaults
                name = "Anonymous User"  # Store anonymous identifier
                answers = data.get('answers', {})
                ministries = data.get('ministries', [])
                situation = data.get('situation', [])
                states = data.get('states', [])  # New states array
                interests = data.get('interests', [])  # New interests array
                
                cur.execute('''
                    INSERT INTO ministry_submissions 
                    (name, email, age_group, gender, state_in_life, interest, situation, recommended_ministries, ip_address)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    name,
                    email,
                    answers.get('age', ''),
                    answers.get('gender', ''),
                    json.dumps(states),  # Store states array as JSON
                    json.dumps(interests),  # Store interests array as JSON
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
                'message': f'Database connection issue. Please try again or contact the parish office at (615) 833-5520.'
            }), 500
            
        except Exception as e:
            logger.error(f"Unexpected error in submit_ministry_interest: {e}")
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred. Please try again or contact the parish office.'
            }), 500

    @app.route('/api/submissions', methods=['GET'])
    @require_admin_auth
    def get_submissions():
        """Admin endpoint to view submissions - NOW REQUIRES AUTHENTICATION"""
        try:
            with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
                cur.execute('''
                    SELECT id, name, email, age_group, gender, state_in_life, interest, 
                           situation, recommended_ministries, submitted_at, ip_address
                    FROM ministry_submissions
                    ORDER BY submitted_at DESC
                ''')
                
                submissions = []
                for row in cur.fetchall():
                    submission = dict(row)
                    
                    # Handle JSONB/JSON fields safely
                    try:
                        if submission['situation']:
                            if isinstance(submission['situation'], str):
                                try:
                                    submission['situation'] = json.loads(submission['situation'])
                                except json.JSONDecodeError:
                                    submission['situation'] = []
                            elif not isinstance(submission['situation'], list):
                                submission['situation'] = []
                        else:
                            submission['situation'] = []
                    except Exception:
                        submission['situation'] = []
                    
                    try:
                        if submission['state_in_life']:
                            if isinstance(submission['state_in_life'], str):
                                try:
                                    submission['state_in_life'] = json.loads(submission['state_in_life'])
                                except json.JSONDecodeError:
                                    submission['state_in_life'] = []
                            elif not isinstance(submission['state_in_life'], list):
                                submission['state_in_life'] = []
                        else:
                            submission['state_in_life'] = []
                    except Exception:
                        submission['state_in_life'] = []
                    
                    try:
                        if submission['interest']:
                            if isinstance(submission['interest'], str):
                                try:
                                    submission['interest'] = json.loads(submission['interest'])
                                except json.JSONDecodeError:
                                    # If it's not JSON, it might be a single string value
                                    submission['interest'] = [submission['interest']] if submission['interest'] else []
                            elif not isinstance(submission['interest'], list):
                                submission['interest'] = []
                        else:
                            submission['interest'] = []
                    except Exception:
                        submission['interest'] = []
                    
                    try:
                        if submission['recommended_ministries']:
                            if isinstance(submission['recommended_ministries'], str):
                                try:
                                    submission['recommended_ministries'] = json.loads(submission['recommended_ministries'])
                                except json.JSONDecodeError:
                                    submission['recommended_ministries'] = []
                            elif not isinstance(submission['recommended_ministries'], list):
                                submission['recommended_ministries'] = []
                        else:
                            submission['recommended_ministries'] = []
                    except Exception:
                        submission['recommended_ministries'] = []
                    
                    if submission['submitted_at']:
                        submission['submitted_at'] = submission['submitted_at'].isoformat()
                    
                    submissions.append(submission)
            
            return jsonify(submissions)
            
        except Exception as e:
            logger.error(f"Error getting submissions: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/admin')
    @require_admin_auth
    def admin_dashboard():
        """Modern Admin dashboard with St. Edward branding"""
        return render_template('admin.html')

    @app.route('/api/clear-all-data', methods=['POST'])
    @require_admin_auth
    def clear_all_data():
        """Admin endpoint to clear all submission data - REQUIRES AUTHENTICATION"""
        try:
            with get_db_connection() as (conn, cur):
                # Get count before deletion for confirmation
                cur.execute('SELECT COUNT(*) FROM ministry_submissions')
                count_before = cur.fetchone()[0]
                
                # Clear all data from the submissions table
                cur.execute('DELETE FROM ministry_submissions')
                
                # Reset the auto-increment counter
                cur.execute('ALTER SEQUENCE ministry_submissions_id_seq RESTART WITH 1')
            
            logger.info(f"Admin cleared all data: {count_before} records deleted")
            
            return jsonify({
                'success': True,
                'message': f'Successfully cleared {count_before} submission records',
                'records_deleted': count_before
            })
            
        except Exception as e:
            logger.error(f"Error clearing all data: {e}")
            return jsonify({
                'success': False,
                'message': f'Database error: {str(e)}'
            }), 500

    @app.route('/test-db')
    def test_database():
        """Test database connection and table structure"""
        try:
            with get_db_connection() as (conn, cur):
                # Test table exists
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'ministry_submissions'")
                table_exists = cur.fetchone()
                
                # Test table structure
                cur.execute("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'ministry_submissions'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
            
            return jsonify({
                'status': 'success',
                'table_exists': bool(table_exists),
                'columns': [{'name': col[0], 'type': col[1], 'nullable': col[2]} for col in columns]
            })
            
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }), 500

    @app.route('/api/get-ministries', methods=['POST'])
    def get_ministries():
        """Protected endpoint to get ministry data"""
        try:
            # Simple protection - could enhance later
            return jsonify(MINISTRY_DATA)
        except Exception as e:
            logger.error(f"Error getting ministries: {e}")
            return jsonify({}), 500
            
    @app.route('/health')
    def health_check():
        """Health check endpoint for Render"""
        try:
            # Test database connection
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
    
    @app.route('/api/submit-contact', methods=['POST'])
    def submit_contact():
        """Handle contact form submissions with quiz results"""
        try:
            # Get client IP address
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            if ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()
            
            # Check rate limit (same as quiz)
            if not check_rate_limit(ip_address):
                logger.warning(f"Rate limit exceeded for contact form from IP: {ip_address}")
                return jsonify({
                    'success': False,
                    'message': 'Too many submissions from this location. Please try again in an hour.'
                }), 429
            
            data = request.json
            logger.info(f"Received contact form from IP {ip_address}: {data.get('name', 'Unknown')}")
            
            with get_db_connection() as (conn, cur):
                # Create contact_submissions table if it doesn't exist
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
                
                # Insert contact submission
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

    @app.route('/admin/contacts')
    @require_admin_auth
    def admin_contacts():
        """Admin endpoint to view contact submissions"""
        try:
            with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
                cur.execute('''
                    SELECT id, name, email, phone, message, quiz_results, 
                           submitted_at, contacted
                    FROM contact_submissions
                    ORDER BY submitted_at DESC
                ''')
                
                contacts = []
                for row in cur.fetchall():
                    contact = dict(row)
                    if contact['submitted_at']:
                        contact['submitted_at'] = contact['submitted_at'].isoformat()
                    contacts.append(contact)
            
            return jsonify(contacts)
            
        except Exception as e:
            logger.error(f"Error getting contact submissions: {e}")
            return jsonify({'error': str(e)}), 500
