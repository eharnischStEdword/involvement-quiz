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
        """Admin dashboard - NOW REQUIRES AUTHENTICATION"""
        admin_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>St. Edward Ministry Submissions - Admin Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
                .header { background: #005921; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
                h1 { color: white; margin: 0; }
                .logout { float: right; color: #ccc; text-decoration: none; }
                .logout:hover { color: white; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 12px; }
                th, td { border: 1px solid #ddd; padding: 6px; text-align: left; }
                th { background-color: #005921; color: white; position: sticky; top: 0; }
                .ministries, .situation, .states, .interests { max-width: 150px; word-wrap: break-word; font-size: 10px; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
                .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #005921; }
                .stat-number { font-size: 2em; font-weight: bold; color: #005921; }
                .export-btn { background: #005921; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 5px; }
                .export-btn:hover { background: #004a1e; }
                .recent { color: #e74c3c; font-weight: bold; }
                .error-message { color: #dc3545; padding: 20px; text-align: center; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ St. Edward Ministry Finder - Admin Dashboard</h1>
                    <p>Secure access to ministry submissions and analytics</p>
                </div>
                
                <div class="stats" id="stats"></div>
                
                <div style="margin: 20px 0;">
                    <button class="export-btn" onclick="exportToCSV()">📊 Export to CSV</button>
                    <button class="export-btn" onclick="location.reload()">🔄 Refresh Data</button>
                </div>
                
                <div id="submissions"></div>
            </div>
            
            <script>
                function exportToCSV() {
                    fetch('/api/submissions')
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Failed to fetch data');
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (!Array.isArray(data)) {
                                throw new Error('Invalid data format');
                            }
                            const csvContent = convertToCSV(data);
                            const blob = new Blob([csvContent], { type: 'text/csv' });
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = 'st_edward_ministry_submissions_' + new Date().toISOString().split('T')[0] + '.csv';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            window.URL.revokeObjectURL(url);
                        })
                        .catch(error => {
                            alert('Error exporting data: ' + error.message);
                        });
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
                
                // Load submissions
                fetch('/api/submissions')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Server error: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Ensure data is an array
                        if (!Array.isArray(data)) {
                            console.error('Data received:', data);
                            throw new Error('Invalid data format - expected array');
                        }
                        
                        // Calculate stats
                        const totalSubmissions = data.length;
                        const last24h = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 24*60*60*1000)).length;
                        const avgMinistries = totalSubmissions > 0 ? 
                            (data.reduce((sum, s) => sum + (Array.isArray(s.recommended_ministries) ? s.recommended_ministries.length : 0), 0) / totalSubmissions).toFixed(1) : 
                            0;
                        
                        // Show stats
                        document.getElementById('stats').innerHTML = `
                            <div class="stat-card">
                                <div class="stat-number">${totalSubmissions}</div>
                                <div>Total Submissions</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${last24h}</div>
                                <div>Last 24 Hours</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${avgMinistries}</div>
                                <div>Avg Ministries per User</div>
                            </div>
                        `;
                        
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
                        console.error('Error:', error);
                        document.getElementById('submissions').innerHTML = `
                            <div class="error-message">
                                <h3>Error loading submissions</h3>
                                <p>${error.message}</p>
                                <p>Please check your authentication or try refreshing the page.</p>
                            </div>
                        `;
                    });
            </script>
        </body>
        </html>
        '''
        return admin_html

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
