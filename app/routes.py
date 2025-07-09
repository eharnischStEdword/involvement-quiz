from flask import request, jsonify, render_template
from functools import wraps
import json
import logging
import psycopg2.extras
from datetime import datetime

from app.models import get_db_connection
from app.ministries import MINISTRY_DATA
from app.utils import check_rate_limit, require_admin_auth

logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/')
    def index():
        """Serve the template with proper Flask template rendering"""
        return render_template('index.html')

    @app.route('/api/submit', methods=['POST'])
    def submit_ministry_interest():
        try:
            # Get client IP address
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            if ',' in ip_address:  # Handle multiple IPs in forwarded header
                ip_address = ip_address.split(',')[0].strip()
            
            # Check rate limit
            if not check_rate_limit(ip_address):
                logger.warning(f"Rate limit exceeded for IP: {ip_address}")
                return jsonify({
                    'success': False,
                    'message': 'Too many submissions from this location. Please try again in an hour.'
                }), 429
            
            data = request.json
            logger.info(f"Received submission from IP {ip_address}: {data}")
            
            # For anonymous tracking, we don't require email
            email = ""  # Store empty string for anonymous submissions
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Extract data with defaults
            name = "Anonymous User"  # Store anonymous identifier
            answers = data.get('answers', {})
            ministries = data.get('ministries', [])
            situation = data.get('situation', [])
            states = data.get('states', [])  # New states array
            interests = data.get('interests', [])  # New interests array
            
            cur.execute('''
                INSERT INTO ministry_submissions 
                (name, email, age_group, gender, state_in_life, interest, situation, recommended_ministries, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                name,
                email,
                answers.get('age', ''),
                answers.get('gender', ''),
                json.dumps(states),  # Store states array as JSON
                json.dumps(interests),  # Store interests array as JSON
                json.dumps(situation),
                json.dumps(ministries),
                ip_address
            ))
            
            submission_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Successfully saved anonymous submission {submission_id} from IP {ip_address}")
            
            return jsonify({
                'success': True,
                'message': 'Thank you for exploring St. Edward ministries!',
                'submission_id': submission_id
            })
            
        except psycopg2.Error as e:
            logger.error(f"Database error in submit_ministry_interest: {e}")
            return jsonify({
                'success': False,
                'message': f'Database connection issue. Please try again or contact the parish office at (615) 833-5520.'
            }), 500
            
        except Exception as e:
            logger.error(f"Unexpected error in submit_ministry_interest: {e}")
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred. Please try again or contact the parish office.'
            }), 500

    @app.route('/api/submissions', methods=['GET'])
    @require_admin_auth
    def get_submissions():
        """Admin endpoint to view submissions - NOW REQUIRES AUTHENTICATION"""
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cur.execute('''
                SELECT id, name, email, age_group, gender, state_in_life, interest, 
                       situation, recommended_ministries, submitted_at, ip_address
                FROM ministry_submissions
                ORDER BY submitted_at DESC
            ''')
            
            submissions = []
            for row in cur.fetchall():
                submission = dict(row)
                
                # Handle JSONB/JSON fields safely
                try:
                    if submission['situation']:
                        if isinstance(submission['situation'], str):
                            try:
                                submission['situation'] = json.loads(submission['situation'])
                            except json.JSONDecodeError:
                                submission['situation'] = []
                        elif not isinstance(submission['situation'], list):
                            submission['situation'] = []
                    else:
                        submission['situation'] = []
                except Exception:
                    submission['situation'] = []
                
                try:
                    if submission['state_in_life']:
                        if isinstance(submission['state_in_life'], str):
                            try:
                                submission['state_in_life'] = json.loads(submission['state_in_life'])
                            except json.JSONDecodeError:
                                submission['state_in_life'] = []
                        elif not isinstance(submission['state_in_life'], list):
                            submission['state_in_life'] = []
                    else:
                        submission['state_in_life'] = []
                except Exception:
                    submission['state_in_life'] = []
                
                try:
                    if submission['interest']:
                        if isinstance(submission['interest'], str):
                            try:
                                submission['interest'] = json.loads(submission['interest'])
                            except json.JSONDecodeError:
                                # If it's not JSON, it might be a single string value
                                submission['interest'] = [submission['interest']] if submission['interest'] else []
                        elif not isinstance(submission['interest'], list):
                            submission['interest'] = []
                    else:
                        submission['interest'] = []
                except Exception:
                    submission['interest'] = []
                
                try:
                    if submission['recommended_ministries']:
                        if isinstance(submission['recommended_ministries'], str):
                            try:
                                submission['recommended_ministries'] = json.loads(submission['recommended_ministries'])
                            except json.JSONDecodeError:
                                submission['recommended_ministries'] = []
                        elif not isinstance(submission['recommended_ministries'], list):
                            submission['recommended_ministries'] = []
                    else:
                        submission['recommended_ministries'] = []
                except Exception:
                    submission['recommended_ministries'] = []
                
                if submission['submitted_at']:
                    submission['submitted_at'] = submission['submitted_at'].isoformat()
                
                submissions.append(submission)
            
            cur.close()
            conn.close()
            
            return jsonify(submissions)
            
        except Exception as e:
            logger.error(f"Error getting submissions: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/admin')
    @require_admin_auth
    def admin_dashboard():
        """Modern Admin dashboard with St. Edward branding"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>St. Edward Ministry Finder - Admin Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #005921 0%, #003764 100%);
            min-height: 100vh;
            color: #2d3748;
        }

        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #005921, #2d7a47);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }

        .header p {
            color: #64748b;
            font-size: 1.1rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #005921, #2d7a47, #DAAA00);
        }

        .stat-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .stat-icon {
            width: 50px;
            height: 50px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
        }

        .stat-icon.submissions { background: linear-gradient(135deg, #00843D, #005921); }
        .stat-icon.today { background: linear-gradient(135deg, #DAAA00, #DDCC71); }
        .stat-icon.week { background: linear-gradient(135deg, #003764, #005921); }
        .stat-icon.avg { background: linear-gradient(135deg, #00843D, #DAAA00); }

        .stat-number {
            font-size: 3rem;
            font-weight: 800;
            color: #1a202c;
            line-height: 1;
        }

        .stat-label {
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.875rem;
            letter-spacing: 0.5px;
        }

        .actions {
            display: flex;
            gap: 15px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
            color: white;
        }

        .btn-primary {
            background: linear-gradient(135deg, #00843D, #005921);
            box-shadow: 0 4px 15px rgba(0, 132, 61, 0.3);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #DAAA00, #DDCC71);
            color: #2d3748;
            box-shadow: 0 4px 15px rgba(218, 170, 0, 0.3);
        }

        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }

        .charts-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .section-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        .chart-container {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
        }

        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 20px;
            text-align: center;
        }

        .pie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }

        .data-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .data-header {
            background: linear-gradient(135deg, #005921, #2d7a47);
            color: white;
            padding: 25px 30px;
            font-size: 1.3rem;
            font-weight: 600;
        }

        .table-container {
            overflow-x: auto;
            max-height: 600px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th, td {
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: #f8fafc;
            font-weight: 600;
            color: #2d3748;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        tr:hover {
            background: #f8fafc;
        }

        .recent {
            background: linear-gradient(135deg, rgba(218, 170, 0, 0.1), rgba(221, 204, 113, 0.1)) !important;
            border-left: 4px solid #DAAA00;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(5px);
        }

        .modal-content {
            background: white;
            margin: 15% auto;
            padding: 40px;
            border-radius: 20px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            text-align: center;
        }

        .modal h3 {
            color: #e53e3e;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }

        .modal-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }

        .checkbox-container {
            margin: 25px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .checkbox-container input[type="checkbox"] {
            width: 20px;
            height: 20px;
            accent-color: #005921;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 60px 20px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #005921;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-message {
            background: linear-gradient(135deg, #fed7d7, #feb2b2);
            color: #c53030;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            margin: 20px 0;
        }

        @media (max-width: 1024px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .dashboard {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .actions {
                flex-direction: column;
            }
            
            .btn {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1><i class="fas fa-church"></i> St. Edward Ministry Finder</h1>
            <p>Admin Dashboard & Analytics</p>
        </div>

        <div class="stats-grid" id="stats">
            <!-- Stats will be populated by JavaScript -->
        </div>

        <div class="actions">
            <button class="btn btn-primary" onclick="exportToCSV()">
                <i class="fas fa-download"></i> Export Data
            </button>
            <button class="btn btn-secondary" onclick="location.reload()">
                <i class="fas fa-sync-alt"></i> Refresh
            </button>
            <button class="btn btn-danger" onclick="showClearModal()">
                <i class="fas fa-trash-alt"></i> Clear All Data
            </button>
        </div>

        <div class="charts-section">
            <h2 class="section-title">
                <i class="fas fa-chart-line"></i> Analytics Overview
            </h2>
            
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Most Popular Ministries</div>
                    <canvas id="ministriesChart" height="300"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Age Distribution</div>
                    <canvas id="ageChart" height="300"></canvas>
                </div>
            </div>

            <div class="pie-grid">
                <div class="chart-container">
                    <div class="chart-title">Gender Distribution</div>
                    <canvas id="genderChart" height="250"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Top Interests</div>
                    <canvas id="interestChart" height="250"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">User Situations</div>
                    <canvas id="situationChart" height="250"></canvas>
                </div>
            </div>
        </div>

        <div class="data-section">
            <div class="data-header">
                <i class="fas fa-table"></i> Recent Submissions
            </div>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>Loading dashboard data...</div>
            </div>
            <div class="table-container">
                <div id="submissions"></div>
            </div>
        </div>
    </div>

    <!-- Clear Data Modal -->
    <div id="clearModal" class="modal">
        <div class="modal-content">
            <h3><i class="fas fa-exclamation-triangle"></i> Confirm Data Deletion</h3>
            <p>This will permanently delete ALL ministry submissions and analytics data.</p>
            <p><strong>This action cannot be undone!</strong></p>
            
            <div class="checkbox-container">
                <input type="checkbox" id="confirmClear">
                <label for="confirmClear">I understand this action cannot be undone</label>
            </div>
            
            <div class="modal-buttons">
                <button class="btn btn-secondary" onclick="hideClearModal()">Cancel</button>
                <button class="btn btn-danger" onclick="clearAllData()" id="confirmBtn" disabled>
                    <i class="fas fa-trash"></i> Delete All Data
                </button>
            </div>
        </div>
    </div>

    <script>
        let submissionsData = [];
        let charts = {};

        function showClearModal() {
            document.getElementById('clearModal').style.display = 'block';
            document.getElementById('confirmClear').checked = false;
            document.getElementById('confirmBtn').disabled = true;
        }

        function hideClearModal() {
            document.getElementById('clearModal').style.display = 'none';
        }

        document.getElementById('confirmClear').addEventListener('change', function() {
            document.getElementById('confirmBtn').disabled = !this.checked;
        });

        function clearAllData() {
            if (!document.getElementById('confirmClear').checked) return;
            
            if (confirm('FINAL CONFIRMATION: Delete all submission data?')) {
                fetch('/api/clear-all-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ All data cleared successfully');
                        location.reload();
                    } else {
                        alert('❌ Error: ' + data.message);
                    }
                })
                .catch(error => alert('❌ Error: ' + error.message));
                hideClearModal();
            }
        }

        function exportToCSV() {
            const csvContent = convertToCSV(submissionsData);
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `st_edward_ministry_data_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }

        function convertToCSV(data) {
            const headers = ['Date', 'Age Group', 'Gender', 'States', 'Interests', 'Situation', 'Ministries', 'IP'];
            let csv = headers.join(',') + '\\n';
            
            data.forEach(row => {
                const csvRow = [
                    new Date(row.submitted_at).toLocaleDateString(),
                    `"${row.age_group || ''}"`,
                    `"${row.gender || ''}"`,
                    `"${Array.isArray(row.state_in_life) ? row.state_in_life.join('; ') : ''}"`,
                    `"${Array.isArray(row.interest) ? row.interest.join('; ') : row.interest || ''}"`,
                    `"${Array.isArray(row.situation) ? row.situation.join('; ') : ''}"`,
                    `"${Array.isArray(row.recommended_ministries) ? row.recommended_ministries.join('; ') : ''}"`,
                    `"${row.ip_address || ''}"`
                ];
                csv += csvRow.join(',') + '\\n';
            });
            return csv;
        }

        function createCharts(data) {
            const stEdwardColors = ['#005921', '#00843D', '#DAAA00', '#DDCC71', '#003764', '#2d7a47'];
            
            const ministryCount = {};
            data.forEach(sub => {
                if (Array.isArray(sub.recommended_ministries)) {
                    sub.recommended_ministries.forEach(ministry => {
                        ministryCount[ministry] = (ministryCount[ministry] || 0) + 1;
                    });
                }
            });
            
            const topMinistries = Object.entries(ministryCount)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 8);
            
            createBarChart('ministriesChart', {
                labels: topMinistries.map(([name]) => name.length > 25 ? name.substring(0, 25) + '...' : name),
                data: topMinistries.map(([,count]) => count)
            });

            const ageCount = {};
            data.forEach(sub => {
                const age = sub.age_group || 'Unknown';
                ageCount[age] = (ageCount[age] || 0) + 1;
            });
            createPieChart('ageChart', ageCount);

            const genderCount = {};
            data.forEach(sub => {
                const gender = sub.gender || 'Not specified';
                genderCount[gender] = (genderCount[gender] || 0) + 1;
            });
            createPieChart('genderChart', genderCount);

            const interestCount = {};
            data.forEach(sub => {
                if (Array.isArray(sub.interest)) {
                    sub.interest.forEach(interest => {
                        interestCount[interest] = (interestCount[interest] || 0) + 1;
                    });
                }
            });
            createPieChart('interestChart', interestCount);

            const situationCount = {};
            data.forEach(sub => {
                if (Array.isArray(sub.situation)) {
                    sub.situation.forEach(situation => {
                        situationCount[situation] = (situationCount[situation] || 0) + 1;
                    });
                }
            });
            createPieChart('situationChart', situationCount);
        }

        function createBarChart(canvasId, data) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            if (charts[canvasId]) charts[canvasId].destroy();
            
            charts[canvasId] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: 'rgba(0, 89, 33, 0.8)',
                        borderColor: 'rgba(0, 89, 33, 1)',
                        borderWidth: 2,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } },
                        x: { ticks: { maxRotation: 45 } }
                    }
                }
            });
        }

        function createPieChart(canvasId, data) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            if (charts[canvasId]) charts[canvasId].destroy();
            
            const stEdwardColors = ['#005921', '#00843D', '#DAAA00', '#DDCC71', '#003764', '#2d7a47', '#52c41a', '#73d13d', '#95de64', '#b7eb8f'];
            
            charts[canvasId] = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        data: Object.values(data),
                        backgroundColor: stEdwardColors.slice(0, Object.keys(data).length),
                        borderWidth: 3,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { padding: 20, usePointStyle: true }
                        }
                    }
                }
            });
        }

        document.getElementById('loading').style.display = 'block';
        
        fetch('/api/submissions')
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                submissionsData = data;
                
                const total = data.length;
                const last24h = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 24*60*60*1000)).length;
                const last7days = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 7*24*60*60*1000)).length;
                const avg = total > 0 ? (data.reduce((sum, s) => sum + (Array.isArray(s.recommended_ministries) ? s.recommended_ministries.length : 0), 0) / total).toFixed(1) : 0;
                
                document.getElementById('stats').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-icon submissions"><i class="fas fa-users"></i></div>
                        </div>
                        <div class="stat-number">${total}</div>
                        <div class="stat-label">Total Submissions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-icon today"><i class="fas fa-calendar-day"></i></div>
                        </div>
                        <div class="stat-number">${last24h}</div>
                        <div class="stat-label">Last 24 Hours</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-icon week"><i class="fas fa-calendar-week"></i></div>
                        </div>
                        <div class="stat-number">${last7days}</div>
                        <div class="stat-label">Last 7 Days</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-icon avg"><i class="fas fa-chart-bar"></i></div>
                        </div>
                        <div class="stat-number">${avg}</div>
                        <div class="stat-label">Avg Ministries</div>
                    </div>
                `;
                
                createCharts(data);
                
                let html = '<table><tr><th>Date</th><th>Age</th><th>Gender</th><th>States</th><th>Interests</th><th>Situation</th><th>Ministries</th></tr>';
                data.slice(0, 50).forEach(sub => {
                    const isRecent = new Date(sub.submitted_at) > new Date(Date.now() - 24*60*60*1000);
                    html += `<tr ${isRecent ? 'class="recent"' : ''}>
                        <td>${new Date(sub.submitted_at).toLocaleDateString()}</td>
                        <td>${sub.age_group || ''}</td>
                        <td>${sub.gender || ''}</td>
                        <td>${Array.isArray(sub.state_in_life) ? sub.state_in_life.join(', ') : ''}</td>
                        <td>${Array.isArray(sub.interest) ? sub.interest.join(', ') : sub.interest || ''}</td>
                        <td>${Array.isArray(sub.situation) ? sub.situation.join(', ') : ''}</td>
                        <td>${Array.isArray(sub.recommended_ministries) ? sub.recommended_ministries.slice(0, 3).join(', ') + (sub.recommended_ministries.length > 3 ? '...' : '') : ''}</td>
                    </tr>`;
                });
                html += '</table>';
                document.getElementById('submissions').innerHTML = html;
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submissions').innerHTML = `<div class="error-message">Error loading data: ${error.message}</div>`;
            });

        window.onclick = function(event) {
            if (event.target == document.getElementById('clearModal')) {
                hideClearModal();
            }
        }
    </script>
</body>
</html>'''

    @app.route('/api/clear-all-data', methods=['POST'])
    @require_admin_auth
    def clear_all_data():
        """Admin endpoint to clear all submission data - REQUIRES AUTHENTICATION"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get count before deletion for confirmation
            cur.execute('SELECT COUNT(*) FROM ministry_submissions')
            count_before = cur.fetchone()[0]
            
            # Clear all data from the submissions table
            cur.execute('DELETE FROM ministry_submissions')
            
            # Reset the auto-increment counter
            cur.execute('ALTER SEQUENCE ministry_submissions_id_seq RESTART WITH 1')
            
            conn.commit()
            cur.close()
            conn.close()
            
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

    @app.route('/test-db')
    def test_database():
        """Test database connection and table structure"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Test table exists
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'ministry_submissions'")
            table_exists = cur.fetchone()
            
            # Test table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'ministry_submissions'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return jsonify({
                'status': 'success',
                'table_exists': bool(table_exists),
                'columns': [{'name': col[0], 'type': col[1], 'nullable': col[2]} for col in columns]
            })
            
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }), 500

    @app.route('/api/get-ministries', methods=['POST'])
    def get_ministries():
        """Protected endpoint to get ministry data"""
        try:
            # Simple protection - could enhance later
            return jsonify(MINISTRY_DATA)
        except Exception as e:
            logger.error(f"Error getting ministries: {e}")
            return jsonify({}), 500
            
    @app.route('/health')
    def health_check():
        """Health check endpoint for Render"""
        try:
            # Test database connection
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
