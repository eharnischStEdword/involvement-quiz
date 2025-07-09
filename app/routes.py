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
        """Enhanced Admin dashboard with charts and clear data functionality"""
        admin_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>St. Edward Ministry Finder - Admin Dashboard</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                }
                .container { 
                    max-width: 1600px; 
                    margin: 0 auto; 
                    background: white; 
                    min-height: 100vh;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }
                .header { 
                    background: linear-gradient(135deg, #005921 0%, #2d7a47 100%); 
                    color: white; 
                    padding: 30px; 
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                h1 { color: white; margin: 0; font-size: 2rem; }
                .subtitle { font-size: 1.1rem; opacity: 0.9; margin-top: 10px; }
                
                .dashboard-content { padding: 30px; }
                
                /* Stats Cards */
                .stats { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; 
                    margin-bottom: 40px; 
                }
                .stat-card { 
                    background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
                    padding: 25px; 
                    border-radius: 12px; 
                    text-align: center; 
                    border-left: 5px solid #005921;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    transition: transform 0.2s ease;
                }
                .stat-card:hover { transform: translateY(-2px); }
                .stat-number { 
                    font-size: 2.5em; 
                    font-weight: bold; 
                    color: #005921; 
                    margin-bottom: 5px;
                }
                .stat-label { 
                    color: #6c757d; 
                    font-weight: 500;
                    text-transform: uppercase;
                    font-size: 0.9rem;
                    letter-spacing: 0.5px;
                }
                
                /* Action Buttons */
                .action-buttons {
                    display: flex;
                    gap: 15px;
                    margin-bottom: 30px;
                    flex-wrap: wrap;
                }
                .btn {
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    font-size: 0.95rem;
                    transition: all 0.2s ease;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .btn-primary { 
                    background: linear-gradient(135deg, #005921 0%, #2d7a47 100%); 
                    color: white; 
                }
                .btn-primary:hover { 
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(0, 89, 33, 0.3);
                }
                .btn-secondary { 
                    background: #6c757d; 
                    color: white; 
                }
                .btn-secondary:hover { 
                    background: #5a6268;
                    transform: translateY(-2px);
                }
                .btn-danger { 
                    background: #dc3545; 
                    color: white; 
                }
                .btn-danger:hover { 
                    background: #c82333;
                    transform: translateY(-2px);
                }
                
                /* Charts Section */
                .charts-section {
                    margin-bottom: 40px;
                }
                .charts-grid {
                    display: grid;
                    grid-template-columns: 2fr 1fr 1fr;
                    gap: 25px;
                    margin-bottom: 30px;
                }
                .chart-container {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    border: 1px solid #e9ecef;
                }
                .chart-title {
                    font-size: 1.2rem;
                    font-weight: 600;
                    color: #005921;
                    margin-bottom: 20px;
                    text-align: center;
                }
                .pie-charts {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 25px;
                }
                
                /* Data Table */
                .table-section {
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                .table-header {
                    background: #005921;
                    color: white;
                    padding: 20px;
                    font-size: 1.2rem;
                    font-weight: 600;
                }
                table { 
                    border-collapse: collapse; 
                    width: 100%; 
                    font-size: 13px; 
                }
                th, td { 
                    border: 1px solid #dee2e6; 
                    padding: 10px 8px; 
                    text-align: left; 
                }
                th { 
                    background-color: #f8f9fa; 
                    color: #005921; 
                    font-weight: 600;
                    position: sticky; 
                    top: 0; 
                    z-index: 10;
                }
                .ministries, .situation, .states, .interests { 
                    max-width: 150px; 
                    word-wrap: break-word; 
                    font-size: 11px; 
                }
                .recent { 
                    background-color: #fff3cd !important; 
                    font-weight: bold; 
                }
                .error-message { 
                    color: #dc3545; 
                    padding: 30px; 
                    text-align: center; 
                    background: #f8d7da; 
                    border: 1px solid #f5c6cb; 
                    border-radius: 8px; 
                    margin: 20px 0; 
                }
                
                /* Modal Styles */
                .modal {
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                }
                .modal-content {
                    background-color: white;
                    margin: 15% auto;
                    padding: 30px;
                    border-radius: 12px;
                    width: 400px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    text-align: center;
                }
                .modal h3 {
                    color: #dc3545;
                    margin-bottom: 20px;
                    font-size: 1.3rem;
                }
                .modal-buttons {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                }
                .checkbox-container {
                    margin: 20px 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                }
                
                /* Loading Spinner */
                .loading {
                    display: none;
                    text-align: center;
                    padding: 20px;
                }
                .spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #005921;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 15px;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @media (max-width: 1200px) {
                    .charts-grid {
                        grid-template-columns: 1fr;
                    }
                    .pie-charts {
                        grid-template-columns: 1fr 1fr;
                    }
                }
                @media (max-width: 768px) {
                    .charts-grid {
                        grid-template-columns: 1fr;
                    }
                    .pie-charts {
                        grid-template-columns: 1fr;
                    }
                    .action-buttons {
                        flex-direction: column;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ St. Edward Ministry Finder</h1>
                    <div class="subtitle">Admin Dashboard & Analytics</div>
                </div>
                
                <div class="dashboard-content">
                    <!-- Stats Cards -->
                    <div class="stats" id="stats"></div>
                    
                    <!-- Action Buttons -->
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="exportToCSV()">
                            📊 Export to CSV
                        </button>
                        <button class="btn btn-secondary" onclick="location.reload()">
                            🔄 Refresh Data
                        </button>
                        <button class="btn btn-danger" onclick="showClearModal()">
                            🗑️ Clear All Data
                        </button>
                    </div>
                    
                    <!-- Charts Section -->
                    <div class="charts-section">
                        <h2 style="color: #005921; margin-bottom: 25px;">📈 Analytics Dashboard</h2>
                        <div class="charts-grid">
                            <div class="chart-container">
                                <div class="chart-title">Top 5 Most Recommended Ministries</div>
                                <canvas id="ministriesChart"></canvas>
                            </div>
                            <div class="chart-container">
                                <div class="chart-title">Age Groups</div>
                                <canvas id="ageChart"></canvas>
                            </div>
                            <div class="chart-container">
                                <div class="chart-title">Gender Distribution</div>
                                <canvas id="genderChart"></canvas>
                            </div>
                        </div>
                        <div class="pie-charts">
                            <div class="chart-container">
                                <div class="chart-title">State in Life</div>
                                <canvas id="stateChart"></canvas>
                            </div>
                            <div class="chart-container">
                                <div class="chart-title">Top Interests</div>
                                <canvas id="interestChart"></canvas>
                            </div>
                            <div class="chart-container">
                                <div class="chart-title">Situations</div>
                                <canvas id="situationChart"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Data Table -->
                    <div class="table-section">
                        <div class="table-header">
                            📋 Recent Submissions
                        </div>
                        <div class="loading" id="loading">
                            <div class="spinner"></div>
                            Loading data...
                        </div>
                        <div id="submissions"></div>
                    </div>
                </div>
            </div>
            
            <!-- Clear Data Modal -->
            <div id="clearModal" class="modal">
                <div class="modal-content">
                    <h3>⚠️ Clear All Data</h3>
                    <p>This action will permanently delete ALL ministry submissions and analytics data.</p>
                    <p><strong>This cannot be undone!</strong></p>
                    
                    <div class="checkbox-container">
                        <input type="checkbox" id="confirmClear" style="transform: scale(1.2);">
                        <label for="confirmClear" style="font-weight: 600;">I understand this action cannot be undone</label>
                    </div>
                    
                    <div class="modal-buttons">
                        <button class="btn btn-secondary" onclick="hideClearModal()">Cancel</button>
                        <button class="btn btn-danger" onclick="clearAllData()" id="confirmBtn" disabled>Clear All Data</button>
                    </div>
                </div>
            </div>
            
            <script>
                let submissionsData = [];
                let charts = {};
                
                // Modal Functions
                function showClearModal() {
                    document.getElementById('clearModal').style.display = 'block';
                    document.getElementById('confirmClear').checked = false;
                    document.getElementById('confirmBtn').disabled = true;
                }
                
                function hideClearModal() {
                    document.getElementById('clearModal').style.display = 'none';
                }
                
                // Enable/disable confirm button based on checkbox
                document.getElementById('confirmClear').addEventListener('change', function() {
                    document.getElementById('confirmBtn').disabled = !this.checked;
                });
                
                // Clear all data function
                function clearAllData() {
                    if (!document.getElementById('confirmClear').checked) return;
                    
                    if (confirm('FINAL CONFIRMATION: Are you absolutely sure you want to delete all data?')) {
                        fetch('/api/clear-all-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert('✅ All data has been cleared successfully');
                                location.reload();
                            } else {
                                alert('❌ Error clearing data: ' + data.message);
                            }
                        })
                        .catch(error => {
                            alert('❌ Error: ' + error.message);
                        });
                        hideClearModal();
                    }
                }
                
                // CSV Export Function
                function exportToCSV() {
                    const csvContent = convertToCSV(submissionsData);
                    const blob = new Blob([csvContent], { type: 'text/csv' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'st_edward_ministry_submissions_' + new Date().toISOString().split('T')[0] + '.csv';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                }
                
                function convertToCSV(data) {
                    const headers = ['Date', 'Name', 'Email', 'Age Group', 'Gender', 'States', 'Interests', 'Situation', 'Recommended Ministries', 'IP Address'];
                    let csv = headers.join(',') + '\\n';
                    
                    data.forEach(row => {
                        const situation = Array.isArray(row.situation) ? row.situation.join('; ') : '';
                        const states = Array.isArray(row.state_in_life) ? row.state_in_life.join('; ') : '';
                        const interests = Array.isArray(row.interest) ? row.interest.join('; ') : row.interest || '';
                        const ministries = Array.isArray(row.recommended_ministries) ? row.recommended_ministries.join('; ') : '';
                        const csvRow = [
                            new Date(row.submitted_at).toLocaleDateString(),
                            `"${row.name || ''}"`,
                            `"${row.email}"`,
                            `"${row.age_group || ''}"`,
                            `"${row.gender || ''}"`,
                            `"${states}"`,
                            `"${interests}"`,
                            `"${situation}"`,
                            `"${ministries}"`,
                            `"${row.ip_address || ''}"`
                        ];
                        csv += csvRow.join(',') + '\\n';
                    });
                    
                    return csv;
                }
                
                // Chart Creation Functions
                function createChartsFromData(data) {
                    // Top 5 Ministries Chart
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
                        .slice(0, 5);
                    
                    createBarChart('ministriesChart', {
                        labels: topMinistries.map(([name]) => name.length > 20 ? name.substring(0, 20) + '...' : name),
                        data: topMinistries.map(([,count]) => count)
                    }, 'Most Recommended Ministries');
                    
                    // Age Groups Chart
                    const ageCount = {};
                    data.forEach(sub => {
                        const age = sub.age_group || 'Unknown';
                        ageCount[age] = (ageCount[age] || 0) + 1;
                    });
                    createPieChart('ageChart', ageCount);
                    
                    // Gender Chart
                    const genderCount = {};
                    data.forEach(sub => {
                        const gender = sub.gender || 'Not specified';
                        genderCount[gender] = (genderCount[gender] || 0) + 1;
                    });
                    createPieChart('genderChart', genderCount);
                    
                    // State Chart
                    const stateCount = {};
                    data.forEach(sub => {
                        if (Array.isArray(sub.state_in_life)) {
                            sub.state_in_life.forEach(state => {
                                stateCount[state] = (stateCount[state] || 0) + 1;
                            });
                        }
                    });
                    createPieChart('stateChart', stateCount);
                    
                    // Interest Chart
                    const interestCount = {};
                    data.forEach(sub => {
                        if (Array.isArray(sub.interest)) {
                            sub.interest.forEach(interest => {
                                interestCount[interest] = (interestCount[interest] || 0) + 1;
                            });
                        }
                    });
                    createPieChart('interestChart', interestCount);
                    
                    // Situation Chart
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
                
                function createBarChart(canvasId, data, title) {
                    const ctx = document.getElementById(canvasId).getContext('2d');
                    if (charts[canvasId]) charts[canvasId].destroy();
                    
                    charts[canvasId] = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                label: 'Recommendations',
                                data: data.data,
                                backgroundColor: [
                                    '#005921',
                                    '#2d7a47',
                                    '#52c41a',
                                    '#73d13d',
                                    '#95de64'
                                ],
                                borderColor: '#005921',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: { stepSize: 1 }
                                }
                            }
                        }
                    });
                }
                
                function createPieChart(canvasId, data) {
                    const ctx = document.getElementById(canvasId).getContext('2d');
                    if (charts[canvasId]) charts[canvasId].destroy();
                    
                    const colors = [
                        '#005921', '#2d7a47', '#52c41a', '#73d13d', '#95de64',
                        '#b7eb8f', '#d9f7be', '#f6ffed', '#237804', '#389e0d'
                    ];
                    
                    charts[canvasId] = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: Object.keys(data),
                            datasets: [{
                                data: Object.values(data),
                                backgroundColor: colors.slice(0, Object.keys(data).length),
                                borderWidth: 2,
                                borderColor: '#fff'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: { 
                                        font: { size: 11 },
                                        padding: 10
                                    }
                                }
                            }
                        }
                    });
                }
                
                // Load and display data
                document.getElementById('loading').style.display = 'block';
                
                fetch('/api/submissions')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Server error: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        document.getElementById('loading').style.display = 'none';
                        
                        if (!Array.isArray(data)) {
                            throw new Error('Invalid data format - expected array');
                        }
                        
                        submissionsData = data;
                        
                        // Calculate and show stats
                        const totalSubmissions = data.length;
                        const last24h = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 24*60*60*1000)).length;
                        const last7days = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 7*24*60*60*1000)).length;
                        const avgMinistries = totalSubmissions > 0 ? 
                            (data.reduce((sum, s) => sum + (Array.isArray(s.recommended_ministries) ? s.recommended_ministries.length : 0), 0) / totalSubmissions).toFixed(1) : 
                            0;
                        
                        document.getElementById('stats').innerHTML = `
                            <div class="stat-card">
                                <div class="stat-number">${totalSubmissions}</div>
                                <div class="stat-label">Total Submissions</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${last24h}</div>
                                <div class="stat-label">Last 24 Hours</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${last7days}</div>
                                <div class="stat-label">Last 7 Days</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${avgMinistries}</div>
                                <div class="stat-label">Avg Ministries per User</div>
                            </div>
                        `;
                        
                        // Create charts
                        createChartsFromData(data);
                        
                        // Show submissions table
                        let html = '<table><tr><th>Date</th><th>Age</th><th>Gender</th><th>States</th><th>Interests</th><th>Situation</th><th>Recommended Ministries</th><th>IP</th></tr>';
                        data.forEach(sub => {
                            const isRecent = new Date(sub.submitted_at) > new Date(Date.now() - 24*60*60*1000);
                            const situationText = Array.isArray(sub.situation) ? sub.situation.join(', ') : (sub.situation || '');
                            const statesText = Array.isArray(sub.state_in_life) ? sub.state_in_life.join(', ') : (sub.state_in_life || '');
                            const interestsText = Array.isArray(sub.interest) ? sub.interest.join(', ') : (sub.interest || '');
                            const ministriesText = Array.isArray(sub.recommended_ministries) ? sub.recommended_ministries.join(', ') : (sub.recommended_ministries || '');
                            
                            html += `<tr ${isRecent ? 'class="recent"' : ''}>
                                <td>${new Date(sub.submitted_at).toLocaleDateString()} ${new Date(sub.submitted_at).toLocaleTimeString()}</td>
                                <td>${sub.age_group || ''}</td>
                                <td>${sub.gender || ''}</td>
                                <td class="states">${statesText}</td>
                                <td class="interests">${interestsText}</td>
                                <td class="situation">${situationText}</td>
                                <td class="ministries">${ministriesText}</td>
                                <td>${sub.ip_address || ''}</td>
                            </tr>`;
                        });
                        html += '</table>';
                        document.getElementById('submissions').innerHTML = html;
                    })
                    .catch(error => {
                        document.getElementById('loading').style.display = 'none';
                        console.error('Error:', error);
                        document.getElementById('submissions').innerHTML = `
                            <div class="error-message">
                                <h3>Error loading submissions</h3>
                                <p>${error.message}</p>
                                <p>Please check your authentication or try refreshing the page.</p>
                            </div>
                        `;
                    });
                
                // Close modal when clicking outside
                window.onclick = function(event) {
                    const modal = document.getElementById('clearModal');
                    if (event.target == modal) {
                        hideClearModal();
                    }
                }
            </script>
        </body>
        </html>
        '''
        return admin_html

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
