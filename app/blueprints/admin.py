# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

from flask import Blueprint, render_template, jsonify, request, Response
import json
import logging
import psycopg2.extras
import io
import csv

from app.database import get_db_connection
from app.auth import require_admin_auth_enhanced as require_admin_auth, require_csrf_token
from app.error_handlers import create_error_response, DatabaseError

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
                SELECT id, name, age_group, gender, state_in_life, interest, 
                       situation, recommended_ministries, submitted_at
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
        error_response, status_code = create_error_response(DatabaseError("Failed to retrieve submissions", e))
        return jsonify(error_response), status_code

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
        error_response, status_code = create_error_response(DatabaseError("Failed to clear data", e))
        return jsonify(error_response), status_code



@admin_bp.route('/api/submissions/export')
@require_admin_auth
def export_submissions():
    """Export submissions with optional date filtering"""
    try:
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            query = '''
                SELECT id, name, age_group, gender, state_in_life, interest, 
                       situation, recommended_ministries, submitted_at
                FROM ministry_submissions
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
        output = io.StringIO()
        if submissions:
            writer = csv.DictWriter(output, fieldnames=submissions[0].keys())
            writer.writeheader()
            writer.writerows(submissions)
        
        output.seek(0)
        
        return Response(
            output.read(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=ministry_submissions.csv'}
        )
        
    except Exception as e:
        logger.error(f"Error exporting submissions: {e}")
        error_response, status_code = create_error_response(DatabaseError("Failed to export submissions", e))
        return jsonify(error_response), status_code
