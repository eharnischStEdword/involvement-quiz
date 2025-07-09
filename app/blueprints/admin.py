from flask import Blueprint, render_template, jsonify
import json
import logging
import psycopg2.extras

from app.database import get_db_connection
from app.auth import require_admin_auth_enhanced as require_admin_auth, require_csrf_token

admin_bp = Blueprint('admin', __name__, strict_slashes=False)
logger = logging.getLogger(__name__)

@admin_bp.route('/admin')
@require_admin_auth
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin.html')

@admin_bp.route('/api/submissions')  # Changed from /submissions
@require_admin_auth
def get_submissions():
    """Get all submissions for admin view"""
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
                
                # Process JSON fields
                for field in ['situation', 'state_in_life', 'interest', 'recommended_ministries']:
                    try:
                        if submission[field]:
                            if isinstance(submission[field], str):
                                try:
                                    submission[field] = json.loads(submission[field])
                                except json.JSONDecodeError:
                                    if field == 'interest':
                                        submission[field] = [submission[field]] if submission[field] else []
                                    else:
                                        submission[field] = []
                            elif not isinstance(submission[field], list):
                                submission[field] = []
                        else:
                            submission[field] = []
                    except Exception:
                        submission[field] = []
                
                if submission['submitted_at']:
                    submission['submitted_at'] = submission['submitted_at'].isoformat()
                
                submissions.append(submission)
        
        return jsonify(submissions)
        
    except Exception as e:
        logger.error(f"Error getting submissions: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/clear-all-data', methods=['POST'])
@require_admin_auth
@require_csrf_token
def clear_all_data():
    """Clear all submission data"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('SELECT COUNT(*) FROM ministry_submissions')
            count_before = cur.fetchone()[0]
            
            cur.execute('DELETE FROM ministry_submissions')
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

@admin_bp.route('/contacts')
@require_admin_auth
def admin_contacts():
    """View contact submissions"""
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
