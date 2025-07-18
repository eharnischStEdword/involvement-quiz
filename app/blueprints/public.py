# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

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
                       age_groups, genders, states, interests, situations
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
                    'age': row[4] if row[4] else [],
                    'gender': row[5] if row[5] else [],
                    'state': row[6] if row[6] else [],
                    'interest': row[7] if row[7] else [],
                    'situation': row[8] if row[8] else []
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

@public_bp.route('/pwa-test')
def pwa_test():
    """PWA test page for debugging installation issues"""
    return render_template('pwa-test.html')

@public_bp.route('/sw.js')
def service_worker():
    """Serve the service worker from root"""
    from flask import send_file
    return send_file('sw.js', mimetype='application/javascript')
