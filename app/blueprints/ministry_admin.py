from flask import Blueprint, jsonify, request
import json
import logging
from app.database import get_db_connection
from app.auth import require_admin_auth_enhanced as require_admin_auth

ministry_admin_bp = Blueprint('ministry_admin', __name__)
logger = logging.getLogger(__name__)

@ministry_admin_bp.route('/api/admin/ministries')
@require_admin_auth
def list_ministries():
    """List all ministries for admin"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('''
                SELECT id, ministry_key, name, description, active, 
                       created_at, updated_at
                FROM ministries 
                ORDER BY name
            ''')
            
            ministries = []
            for row in cur.fetchall():
                ministries.append({
                    'id': row[0],
                    'key': row[1],
                    'name': row[2],
                    'description': row[3],
                    'active': row[4],
                    'created_at': row[5].isoformat() if row[5] else None,
                    'updated_at': row[6].isoformat() if row[6] else None
                })
            
            return jsonify(ministries)
    except Exception as e:
        logger.error(f"Error listing ministries: {e}")
        return jsonify({'error': str(e)}), 500

@ministry_admin_bp.route('/api/admin/ministries/<int:ministry_id>')
@require_admin_auth
def get_ministry(ministry_id):
    """Get single ministry details"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('''
                SELECT * FROM ministries WHERE id = %s
            ''', (ministry_id,))
            
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'Ministry not found'}), 404
            
            return jsonify({
                'id': row[0],
                'key': row[1],
                'name': row[2],
                'description': row[3],
                'details': row[4],
                'age_groups': json.loads(row[5]) if row[5] else [],
                'genders': json.loads(row[6]) if row[6] else [],
                'states': json.loads(row[7]) if row[7] else [],
                'interests': json.loads(row[8]) if row[8] else [],
                'situations': json.loads(row[9]) if row[9] else [],
                'active': row[10]
            })
    except Exception as e:
        logger.error(f"Error getting ministry: {e}")
        return jsonify({'error': str(e)}), 500

@ministry_admin_bp.route('/api/admin/ministries/<int:ministry_id>', methods=['PUT'])
@require_admin_auth
def update_ministry(ministry_id):
    """Update ministry details"""
    try:
        data = request.json
        
        with get_db_connection() as (conn, cur):
            cur.execute('''
                UPDATE ministries SET
                    name = %s,
                    description = %s,
                    details = %s,
                    age_groups = %s,
                    genders = %s,
                    states = %s,
                    interests = %s,
                    situations = %s,
                    active = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (
                data.get('name'),
                data.get('description', ''),
                data.get('details', ''),
                json.dumps(data.get('age_groups', [])),
                json.dumps(data.get('genders', [])),
                json.dumps(data.get('states', [])),
                json.dumps(data.get('interests', [])),
                json.dumps(data.get('situations', [])),
                data.get('active', True),
                ministry_id
            ))
            
            if cur.rowcount == 0:
                return jsonify({'error': 'Ministry not found'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating ministry: {e}")
        return jsonify({'error': str(e)}), 500

@ministry_admin_bp.route('/api/admin/ministries/<int:ministry_id>/toggle', methods=['POST'])
@require_admin_auth
def toggle_ministry(ministry_id):
    """Toggle ministry active status"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('''
                UPDATE ministries 
                SET active = NOT active, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING active
            ''', (ministry_id,))
            
            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Ministry not found'}), 404
            
            return jsonify({'success': True, 'active': result[0]})
    except Exception as e:
        logger.error(f"Error toggling ministry: {e}")
        return jsonify({'error': str(e)}), 500
