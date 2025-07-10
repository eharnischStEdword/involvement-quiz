from flask import Blueprint, render_template, jsonify
import json
import logging
import psycopg2.extras

from app.database import get_db_connection
from app.auth import require_admin_auth_enhanced as require_admin_auth, require_csrf_token

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@admin_bp.route('/admin')
@admin_bp.route('/admin/')
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

# Add this route to app/blueprints/admin.py after the admin_contacts function

@admin_bp.route('/api/contacts/<int:contact_id>/mark-contacted', methods=['POST'])
@require_admin_auth
def mark_contact_contacted(contact_id):
    """Mark a contact as contacted"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute(
                "UPDATE contact_submissions SET contacted = TRUE WHERE id = %s",
                (contact_id,)
            )
            
            if cur.rowcount == 0:
                return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        logger.info(f"Contact {contact_id} marked as contacted")
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error marking contact as contacted: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add this route for date-filtered CSV export

@admin_bp.route('/api/submissions/export')
@require_admin_auth
def export_submissions():
    """Export submissions with optional date filtering"""
    try:
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            query = '''
                SELECT * FROM ministry_submissions
                WHERE 1=1
            '''
            params = []
            
            if date_from:
                query += ' AND submitted_at >= %s'
                params.append(date_from)
            
            if date_to:
                query += ' AND submitted_at <= %s'
                params.append(f"{date_to} 23:59:59")
            
            query += ' ORDER BY submitted_at DESC'
            
            cur.execute(query, params)
            submissions = cur.fetchall()
        
        # Convert to CSV
        import io
        import csv
        
        output = io.StringIO()
        if submissions:
            writer = csv.DictWriter(output, fieldnames=submissions[0].keys())
            writer.writeheader()
            writer.writerows(submissions)
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.read(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=ministry_submissions.csv'}
        )
        
    except Exception as e:
        logger.error(f"Error exporting submissions: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/contacts/<int:contact_id>/mark-contacted', methods=['POST'])
@require_admin_auth
