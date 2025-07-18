# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

from flask import Blueprint, render_template, jsonify, request, Response
import json
import logging
import psycopg2.extras
from datetime import datetime
import csv
import io

from app.database import get_db_connection
from app.auth import require_admin_auth_enhanced as require_admin_auth
from app.error_handlers import create_error_response, DatabaseError, ValidationError

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
                if ministry.get(field):
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
        if not data:
            error_response, status_code = create_error_response(ValidationError("No data provided"))
            return jsonify(error_response), status_code
        
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
        if not data:
            error_response, status_code = create_error_response(ValidationError("No data provided"))
            return jsonify(error_response), status_code
        
        with get_db_connection() as (conn, cur):
            # Check if ministry exists
            cur.execute('SELECT id FROM ministries WHERE id = %s', (ministry_id,))
            if not cur.fetchone():
                return jsonify({'success': False, 'error': 'Ministry not found'}), 404
            
            # Check if updated_at column exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'ministries' AND column_name = 'updated_at'
            """)
            has_updated_at = cur.fetchone() is not None
            
            # Update ministry
            if has_updated_at:
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
            else:
                cur.execute('''
                    UPDATE ministries 
                    SET ministry_key = %s, name = %s, description = %s, details = %s,
                        age_groups = %s, genders = %s, states = %s, interests = %s,
                        situations = %s, active = %s
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
            # Check if updated_at exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'ministries' AND column_name = 'updated_at'
            """)
            has_updated_at = cur.fetchone() is not None
            
            # Soft delete by setting active to false
            if has_updated_at:
                cur.execute('''
                    UPDATE ministries 
                    SET active = false, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING name
                ''', (ministry_id,))
            else:
                cur.execute('''
                    UPDATE ministries 
                    SET active = false
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
            # Check if updated_at exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'ministries' AND column_name = 'updated_at'
            """)
            has_updated_at = cur.fetchone() is not None
            
            if has_updated_at:
                cur.execute('''
                    UPDATE ministries 
                    SET active = NOT active, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING name, active
                ''', (ministry_id,))
            else:
                cur.execute('''
                    UPDATE ministries 
                    SET active = NOT active
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

@ministry_admin_bp.route('/api/ministries/bulk-update', methods=['POST'])
@require_admin_auth
def bulk_update_ministries():
    """Update multiple ministries at once"""
    try:
        data = request.json
        ministry_ids = data.get('ministry_ids', [])
        updates = data.get('updates', {})
        
        if not ministry_ids:
            return jsonify({'success': False, 'error': 'No ministries selected'}), 400
        
        updated_count = 0
        errors = []
        
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            # Check if updated_at exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'ministries' AND column_name = 'updated_at'
            """)
            has_updated_at = cur.fetchone() is not None
            
            for ministry_id in ministry_ids:
                try:
                    # Get current ministry data
                    cur.execute('SELECT * FROM ministries WHERE id = %s', (ministry_id,))
                    ministry = cur.fetchone()
                    
                    if not ministry:
                        errors.append(f"Ministry {ministry_id} not found")
                        continue
                    
                    # Apply updates
                    updated_data = {}
                    
                    # Handle adding categories
                    if 'add' in updates:
                        for field, values in updates['add'].items():
                            current = ministry.get(field, [])
                            updated_data[field] = list(set(current + values))
                    
                    # Handle removing categories
                    if 'remove' in updates:
                        for field, values in updates['remove'].items():
                            current = ministry.get(field, [])
                            updated_data[field] = [item for item in current if item not in values]
                    
                    # Handle direct updates
                    if 'set' in updates:
                        updated_data.update(updates['set'])
                    
                    # Update the ministry
                    if updated_data:
                        set_clause = ', '.join([f"{k} = %s" for k in updated_data.keys()])
                        if has_updated_at:
                            set_clause += ', updated_at = CURRENT_TIMESTAMP'
                        
                        values = [json.dumps(v) if isinstance(v, list) else v for v in updated_data.values()]
                        values.append(ministry_id)
                        
                        cur.execute(f'''
                            UPDATE ministries 
                            SET {set_clause}
                            WHERE id = %s
                        ''', values)
                        
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Ministry {ministry_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Updated {updated_count} ministries',
            'updated': updated_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
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
            # Check if updated_at exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'ministries' AND column_name = 'updated_at'
            """)
            has_updated_at = cur.fetchone() is not None
            
            for ministry in ministries_data:
                try:
                    if has_updated_at:
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
                    else:
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
                                active = EXCLUDED.active
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

@ministry_admin_bp.route('/api/ministries/export-csv')
@require_admin_auth
def export_ministries_csv():
    """Export all ministries as CSV"""
    try:
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            cur.execute('''
                SELECT ministry_key, name, description, details, 
                       age_groups, genders, states, interests, situations, active
                FROM ministries
                ORDER BY name
            ''')
            
            ministries = cur.fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = ['ministry_key', 'name', 'description', 'details', 
                  'age_groups', 'genders', 'states', 'interests', 'situations', 'active']
        writer.writerow(headers)
        
        # Write data
        for ministry in ministries:
            row = [
                ministry['ministry_key'],
                ministry['name'],
                ministry['description'] or '',
                ministry['details'] or '',
                '|'.join(ministry['age_groups'] or []),  # Pipe-separated for multi-values
                '|'.join(ministry['genders'] or []),
                '|'.join(ministry['states'] or []),
                '|'.join(ministry['interests'] or []),
                '|'.join(ministry['situations'] or []),
                'true' if ministry['active'] else 'false'
            ]
            writer.writerow(row)
        
        output.seek(0)
        
        return Response(
            output.read(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=ministries_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting ministries: {e}")
        return jsonify({'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries/export-python')
@require_admin_auth
def export_ministries_python():
    """Export active ministries as Python code for MINISTRY_DATA fallback"""
    try:
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            # Only export active ministries
            cur.execute('''
                SELECT ministry_key, name, description, details, 
                       age_groups, genders, states, interests, situations
                FROM ministries
                WHERE active = true
                ORDER BY ministry_key
            ''')
            
            ministries = cur.fetchall()
        
        # Build Python code
        output = io.StringIO()
        output.write("# © 2024–2025 Harnisch LLC. All Rights Reserved.\n")
        output.write("# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).\n")
        output.write("# Unauthorized use, distribution, or modification is prohibited.\n\n")
        output.write("# Generated from database on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        output.write("MINISTRY_DATA = {\n")
        
        for i, ministry in enumerate(ministries):
            # Properly format the key
            output.write(f"    '{ministry['ministry_key']}': {{\n")
            output.write(f"        'name': {repr(ministry['name'])},\n")
            
            if ministry['description']:
                output.write(f"        'description': {repr(ministry['description'])},\n")
            
            if ministry['details']:
                output.write(f"        'details': {repr(ministry['details'])},\n")
            
            # Convert database arrays to Python lists with proper names
            if ministry['age_groups']:
                output.write(f"        'age': {ministry['age_groups']},\n")
            
            if ministry['genders']:
                output.write(f"        'gender': {ministry['genders']},\n")
            
            if ministry['states']:
                output.write(f"        'state': {ministry['states']},\n")
            
            if ministry['interests']:
                output.write(f"        'interest': {ministry['interests']},\n")
            
            if ministry['situations']:
                output.write(f"        'situation': {ministry['situations']},\n")
            
            # Close the ministry dict
            output.write("    }")
            
            # Add comma if not last item
            if i < len(ministries) - 1:
                output.write(",")
            
            output.write("\n")
        
        output.write("}\n")
        
        output.seek(0)
        
        return Response(
            output.read(),
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename=ministries_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting ministries as Python: {e}")
        return jsonify({'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries/import-csv', methods=['POST'])
@require_admin_auth
def import_ministries_csv():
    """Import ministries from CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be CSV format'}), 400
        
        # Read CSV
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        imported_count = 0
        updated_count = 0
        errors = []
        
        with get_db_connection() as (conn, cur):
            # Check if updated_at exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'ministries' AND column_name = 'updated_at'
            """)
            has_updated_at = cur.fetchone() is not None
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header
                try:
                    # Parse pipe-separated values
                    age_groups = [x.strip() for x in row.get('age_groups', '').split('|') if x.strip()]
                    genders = [x.strip() for x in row.get('genders', '').split('|') if x.strip()]
                    states = [x.strip() for x in row.get('states', '').split('|') if x.strip()]
                    interests = [x.strip() for x in row.get('interests', '').split('|') if x.strip()]
                    situations = [x.strip() for x in row.get('situations', '').split('|') if x.strip()]
                    
                    # Check if ministry exists
                    cur.execute('SELECT id FROM ministries WHERE ministry_key = %s', (row['ministry_key'],))
                    exists = cur.fetchone()
                    
                    if has_updated_at:
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
                            row['ministry_key'],
                            row['name'],
                            row.get('description', ''),
                            row.get('details', ''),
                            json.dumps(age_groups),
                            json.dumps(genders),
                            json.dumps(states),
                            json.dumps(interests),
                            json.dumps(situations),
                            row.get('active', 'true').lower() == 'true'
                        ))
                    else:
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
                                active = EXCLUDED.active
                        ''', (
                            row['ministry_key'],
                            row['name'],
                            row.get('description', ''),
                            row.get('details', ''),
                            json.dumps(age_groups),
                            json.dumps(genders),
                            json.dumps(states),
                            json.dumps(interests),
                            json.dumps(situations),
                            row.get('active', 'true').lower() == 'true'
                        ))
                    
                    if exists:
                        updated_count += 1
                    else:
                        imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Imported {imported_count} new ministries, updated {updated_count} existing ministries',
            'imported': imported_count,
            'updated': updated_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add this temporary route to app/blueprints/ministry_admin.py
@ministry_admin_bp.route('/api/ministries/debug-db')
@require_admin_auth
def debug_database():
    """Debug database connection"""
    import os
    try:
        with get_db_connection() as (conn, cur):
            cur.execute("SELECT current_database(), version()")
            db_info = cur.fetchone()
            
            cur.execute("SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE active) as active FROM ministries")
            counts = cur.fetchone()
            
            # Get first 5 ministries to verify data
            cur.execute("SELECT id, name, active FROM ministries ORDER BY id LIMIT 5")
            sample = cur.fetchall()
        
        return jsonify({
            'database_url': os.environ.get('DATABASE_URL', 'Not set')[:50] + '...',
            'current_db': db_info[0],
            'postgres_version': db_info[1],
            'total_ministries': counts[0],
            'active_ministries': counts[1],
            'sample_data': sample
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ministry_admin_bp.route('/api/ministries/permanent-delete', methods=['POST'])
@require_admin_auth
def permanent_delete_ministries():
    """Permanently delete ministries from database (DESTRUCTIVE)"""
    try:
        data = request.json
        ministry_ids = data.get('ministry_ids', [])
        
        if not ministry_ids:
            return jsonify({'success': False, 'error': 'No ministries selected'}), 400
        
        deleted_count = 0
        errors = []
        
        with get_db_connection() as (conn, cur):
            # First verify all selected ministries are inactive
            cur.execute('''
                SELECT id, name, active FROM ministries 
                WHERE id = ANY(%s)
            ''', (ministry_ids,))
            
            ministries_to_delete = cur.fetchall()
            
            # Check if any are still active
            active_ministries = [m for m in ministries_to_delete if m[2]]
            if active_ministries:
                return jsonify({
                    'success': False,
                    'error': f'{len(active_ministries)} ministries are still active. Only inactive ministries can be permanently deleted.'
                }), 400
            
            # Permanently delete the ministries
            for ministry_id in ministry_ids:
                try:
                    cur.execute('DELETE FROM ministries WHERE id = %s', (ministry_id,))
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"Ministry {ministry_id}: {str(e)}")
        
        logger.warning(f"PERMANENTLY DELETED {deleted_count} ministries")
        
        return jsonify({
            'success': True,
            'message': f'Permanently deleted {deleted_count} ministries',
            'deleted': deleted_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in permanent delete: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
