from flask import Blueprint, render_template, jsonify
from app.database import get_db_connection
import json
import logging

public_bp = Blueprint('public', __name__)
logger = logging.getLogger(__name__)

@public_bp.route('/')
def index():
    """Serve the main quiz template"""
    return render_template('index.html')

@public_bp.route('/api/get-ministries', methods=['POST'])
def get_ministries():
    """Get active ministries from database"""
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('''
                SELECT ministry_key, name, description, details,
                       age_groups as age, genders as gender, 
                       states as state, interests as interest,
                       situations as situation
                FROM ministries
                WHERE active = true
            ''')
            
            ministries = {}
            for row in cur.fetchall():
                key = row[0]
                ministries[key] = {
                    'name': row[1],
                    'description': row[2],
                    'details': row[3],
                    'age': json.loads(row[4]) if row[4] else [],
                    'gender': json.loads(row[5]) if row[5] else [],
                    'state': json.loads(row[6]) if row[6] else [],
                    'interest': json.loads(row[7]) if row[7] else [],
                    'situation': json.loads(row[8]) if row[8] else []
                }
        
        return jsonify(ministries)
    except Exception as e:
        logger.error(f"Error loading ministries from database: {e}")
        # Fallback to MINISTRY_DATA if database fails
        try:
            from app.ministries import MINISTRY_DATA
            return jsonify(MINISTRY_DATA)
        except:
            return jsonify({})
