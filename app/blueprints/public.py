from flask import Blueprint, render_template, jsonify
from app.ministries import MINISTRY_DATA

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Serve the main quiz template"""
    return render_template('index.html')

@public_bp.route('/api/get-ministries', methods=['POST'])
def get_ministries():
    """Protected endpoint to get ministry data"""
    try:
        return jsonify(MINISTRY_DATA)
    except Exception as e:
        return jsonify({}), 500
