from flask import Blueprint, render_template, jsonify
from app.ministry_loader import load_ministries_from_db

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Serve the main quiz template"""
    return render_template('index.html')

@public_bp.route('/api/get-ministries', methods=['POST'])
def get_ministries():
    """Protected endpoint to get ministry data from database"""
    try:
        ministries = load_ministries_from_db()
        return jsonify(ministries)
    except Exception as e:
        # Fallback to hardcoded data if DB fails
        from app.ministries import MINISTRY_DATA
        return jsonify(MINISTRY_DATA)
