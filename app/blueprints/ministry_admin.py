from flask import Blueprint, render_template, jsonify, request
import json
import logging
import psycopg2.extras
from datetime import datetime

from app.database import get_db_connection
from app.auth import require_admin_auth_enhanced as require_admin_auth

ministry_admin_bp = Blueprint('ministry_admin', __name__)
logger = logging.getLogger(__name__)

@ministry_admin_bp.route('/admin/ministries')
@require_admin_auth
def ministry_manager():
    """Ministry management interface"""
    return render_template('ministry_admin.html')

@ministry_admin_bp.route('/api/ministries/all')
@require_admin_auth
def get_all_ministries():
    """Get all ministries from database"""
    try:
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            # Check if updated_at column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ministries' AND column_name = 'updated_at'
            """)
            has_updated_at = cur.fetchone() is not None
            
            # Build query based on available columns
            if has_updated_at:
                query = '''
                    SELECT id, ministry_key, name, description, details, 
                           age_groups, genders, states, interests, situations,
                           active, created_at, updated_at
                    FROM ministries
                    ORDER BY name
                '''
            else:
                query = '''
                    SELECT id, ministry_key, name, description, details, 
                           age_groups, genders, states, interests, situations,
                           active, created_at
                    FROM ministries
                    ORDER BY name
                '''
            
            cur.execute(query)
            
            ministries = []
            for row in cur.fetchall():
                ministry = dict(row)
                # Convert timestamps to ISO format
                if ministry.get('created_at'):
                    ministry['created_at'] = ministry['created_at'].isoformat()
                if ministry.get('updated_at'):
                    ministry['updated_at'] = ministry['updated_at'].isoformat()
                ministries.append(ministry)
        
        return jsonify({
            'success': True,
            'ministries': ministries,
            'count': len(ministries)
        })
        
    except Exception as e:
        logger.error(f"Error getting ministries: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
@ministry_admin_bp.route('/api/ministries/<int:ministry_id>')
@require_admin_auth
def get_ministry(ministry_id):
    """Get single ministry by ID"""
    try:
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            cur.execute('''
                SELECT * FROM ministries WHERE id = %s
            ''', (ministry_id,))
            
            ministry = cur.fetchone()
            if not ministry:
                return jsonify({'success': False, 'error': 'Ministry not found'}), 404
            
            ministry = dict(ministry)
            for field in ['created_at', 'updated_at']:
                if ministry[field]:
                    ministry[field] = ministry[field].isoformat()
        
        return jsonify({
            'success': True,
            'ministry': ministry
        })
        
    except Exception as e:
        logger.error(f"Error getting ministry {ministry_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries', methods=['POST'])
@require_admin_auth
def create_ministry():
    """Create new ministry"""
    try:
        data = request.json
        
        with get_db_connection() as (conn, cur):
            cur.execute('''
                INSERT INTO ministries 
                (ministry_key, name, description, details, age_groups, 
                 genders, states, interests, situations, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                data.get('ministry_key'),
                data.get('name'),
                data.get('description', ''),
                data.get('details', ''),
                json.dumps(data.get('age_groups', [])),
                json.dumps(data.get('genders', [])),
                json.dumps(data.get('states', [])),
                json.dumps(data.get('interests', [])),
                json.dumps(data.get('situations', [])),
                data.get('active', True)
            ))
            
            ministry_id = cur.fetchone()[0]
        
        logger.info(f"Created new ministry: {data.get('name')} (ID: {ministry_id})")
        
        return jsonify({
            'success': True,
            'message': 'Ministry created successfully',
            'ministry_id': ministry_id
        })
        
    except psycopg2.IntegrityError as e:
        if 'ministry_key' in str(e):
            return jsonify({
                'success': False,
                'error': 'Ministry key already exists'
            }), 400
        return jsonify({'success': False, 'error': str(e)}), 400
        
    except Exception as e:
        logger.error(f"Error creating ministry: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries/<int:ministry_id>', methods=['PUT'])
@require_admin_auth
def update_ministry(ministry_id):
    """Update existing ministry"""
    try:
        data = request.json
        
        with get_db_connection() as (conn, cur):
            # Check if ministry exists
            cur.execute('SELECT id FROM ministries WHERE id = %s', (ministry_id,))
            if not cur.fetchone():
                return jsonify({'success': False, 'error': 'Ministry not found'}), 404
            
            # Update ministry
            cur.execute('''
                UPDATE ministries 
                SET ministry_key = %s, name = %s, description = %s, details = %s,
                    age_groups = %s, genders = %s, states = %s, interests = %s,
                    situations = %s, active = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (
                data.get('ministry_key'),
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
        
        logger.info(f"Updated ministry {ministry_id}: {data.get('name')}")
        
        return jsonify({
            'success': True,
            'message': 'Ministry updated successfully'
        })
        
    except psycopg2.IntegrityError as e:
        if 'ministry_key' in str(e):
            return jsonify({
                'success': False,
                'error': 'Ministry key already exists'
            }), 400
        return jsonify({'success': False, 'error': str(e)}), 400
        
    except Exception as e:
        logger.error(f"Error updating ministry {ministry_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries/<int:ministry_id>', methods=['DELETE'])
@require_admin_auth
def delete_ministry(ministry_id):
    """Delete ministry (soft delete by setting active=false)"""
    try:
        with get_db_connection() as (conn, cur):
            # Soft delete by setting active to false
            cur.execute('''
                UPDATE ministries 
                SET active = false, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING name
            ''', (ministry_id,))
            
            result = cur.fetchone()
            if not result:
                return jsonify({'success': False, 'error': 'Ministry not found'}), 404
            
            ministry_name = result[0]
        
        logger.info(f"Soft deleted ministry {ministry_id}: {ministry_name}")
        
        return jsonify({
            'success': True,
            'message': f'Ministry "{ministry_name}" deactivated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting ministry {ministry_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries/<int:ministry_id>/toggle-active', methods=['POST'])
@require_admin_auth
def toggle_ministry_active(ministry_id):
    """Toggle ministry active status"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('''
                UPDATE ministries 
                SET active = NOT active, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING name, active
            ''', (ministry_id,))
            
            result = cur.fetchone()
            if not result:
                return jsonify({'success': False, 'error': 'Ministry not found'}), 404
            
            ministry_name, is_active = result
        
        logger.info(f"Toggled ministry {ministry_id} active status to {is_active}")
        
        return jsonify({
            'success': True,
            'message': f'Ministry "{ministry_name}" {"activated" if is_active else "deactivated"}',
            'active': is_active
        })
        
    except Exception as e:
        logger.error(f"Error toggling ministry {ministry_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries/bulk-import', methods=['POST'])
@require_admin_auth
def bulk_import_ministries():
    """Import multiple ministries from JSON"""
    try:
        data = request.json
        ministries_data = data.get('ministries', [])
        
        if not ministries_data:
            return jsonify({'success': False, 'error': 'No ministries provided'}), 400
        
        imported_count = 0
        errors = []
        
        with get_db_connection() as (conn, cur):
            for ministry in ministries_data:
                try:
                    cur.execute('''
                        INSERT INTO ministries 
                        (ministry_key, name, description, details, age_groups, 
                         genders, states, interests, situations, active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (ministry_key) DO UPDATE SET
                            name = EXCLUDED.name,
                            description = EXCLUDED.description,
                            details = EXCLUDED.details,
                            age_groups = EXCLUDED.age_groups,
                            genders = EXCLUDED.genders,
                            states = EXCLUDED.states,
                            interests = EXCLUDED.interests,
                            situations = EXCLUDED.situations,
                            active = EXCLUDED.active,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (
                        ministry.get('ministry_key'),
                        ministry.get('name'),
                        ministry.get('description', ''),
                        ministry.get('details', ''),
                        json.dumps(ministry.get('age_groups', ministry.get('age', []))),
                        json.dumps(ministry.get('genders', ministry.get('gender', []))),
                        json.dumps(ministry.get('states', ministry.get('state', []))),
                        json.dumps(ministry.get('interests', ministry.get('interest', []))),
                        json.dumps(ministry.get('situations', ministry.get('situation', []))),
                        ministry.get('active', True)
                    ))
                    imported_count += 1
                except Exception as e:
                    errors.append(f"{ministry.get('name', 'Unknown')}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Imported {imported_count} ministries',
            'imported': imported_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in bulk import: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
