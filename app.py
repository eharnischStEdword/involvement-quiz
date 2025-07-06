from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from functools import wraps
import psycopg2
import psycopg2.extras
import os
from datetime import datetime, timedelta
import json
import logging
import hashlib
import time
import threading
import requests
import pytz

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple rate limiting storage (in production, use Redis)
request_counts = {}
RATE_LIMIT_REQUESTS = 5  # Max 5 submissions per hour per IP
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Admin credentials - SET THESE AS ENVIRONMENT VARIABLES
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'stedward_admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change_this_password_123!')

def check_rate_limit(ip_address):
    """Simple rate limiting - max 5 submissions per hour per IP"""
    current_time = time.time()
    
    # Clean old entries
    cutoff_time = current_time - RATE_LIMIT_WINDOW
    request_counts.update({ip: [t for t in times if t > cutoff_time] 
                          for ip, times in request_counts.items()})
    
    # Check current IP
    if ip_address not in request_counts:
        request_counts[ip_address] = []
    
    request_counts[ip_address] = [t for t in request_counts[ip_address] if t > cutoff_time]
    
    if len(request_counts[ip_address]) >= RATE_LIMIT_REQUESTS:
        return False
    
    request_counts[ip_address].append(current_time)
    return True

def keep_alive():
    """Ping the service every 10 minutes to prevent sleeping"""
    time.sleep(60)  # Wait 1 minute before starting to let app fully start
    
    while True:
        try:
            time.sleep(600)  # Wait 10 minutes
            # Only ping during reasonable hours (7 AM - 11 PM Central Time)
            central = pytz.timezone('US/Central')
            now = datetime.now(central)
            
            # Only keep alive during extended business hours
            if 7 <= now.hour <= 23:  # 7 AM to 11 PM Central
                url = os.environ.get('RENDER_EXTERNAL_URL', 'https://involvement-quiz.onrender.com')
                response = requests.get(f'{url}/health', timeout=30)
                logger.info(f"Keep-alive ping sent - Status: {response.status_code}")
            else:
                logger.info("Outside business hours, allowing sleep")
        except Exception as e:
            logger.error(f"Keep-alive failed: {e}")
            # Continue the loop even if ping fails

def require_admin_auth(f):
    """Decorator for admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
            return ('Admin authentication required', 401, {
                'WWW-Authenticate': 'Basic realm="St. Edward Admin"'
            })
        return f(*args, **kwargs)
    return decorated_function

# Database connection
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            logger.info("Connected to production database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to production database: {e}")
            raise
    else:
        # Local development
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='st_edward_ministries',
                user='your_username',
                password='your_password'
            )
            logger.info("Connected to local database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to local database: {e}")
            raise

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create submissions table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ministry_submissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) NOT NULL,
                age_group VARCHAR(50),
                gender VARCHAR(20),
                state_in_life VARCHAR(50),
                interest VARCHAR(50),
                situation JSONB DEFAULT '[]'::jsonb,
                recommended_ministries TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45)
            )
        ''')
        
        # Add situation column if it doesn't exist
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'situation'
        """)
        if not cur.fetchone():
            cur.execute("ALTER TABLE ministry_submissions ADD COLUMN situation JSONB DEFAULT '[]'::jsonb")
            logger.info("Added situation column to ministry_submissions table")
        
        # Add ip_address column if it doesn't exist
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'ip_address'
        """)
        if not cur.fetchone():
            cur.execute("ALTER TABLE ministry_submissions ADD COLUMN ip_address VARCHAR(45)")
            logger.info("Added ip_address column to ministry_submissions table")
        
        # Create ministries table for easier management
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ministries (
                id SERIAL PRIMARY KEY,
                ministry_key VARCHAR(100) UNIQUE,
                name VARCHAR(255),
                description TEXT,
                details TEXT,
                age_groups TEXT,
                genders TEXT,
                states TEXT,
                interests TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Initialize database on startup
try:
    init_db()
    logger.info("Database initialized on startup")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

# Start keep-alive service (only in production)
if os.environ.get('DATABASE_URL'):  # Only run keep-alive in production
    if not os.environ.get('WERKZEUG_RUN_MAIN'):  # Prevent duplicate threads in debug mode
        try:
            threading.Thread(target=keep_alive, daemon=True).start()
            logger.info("Keep-alive service started for production")
        except Exception as e:
            logger.error(f"Failed to start keep-alive service: {e}")
else:
    logger.info("Local development mode - keep-alive service disabled")

@app.route('/')
def index():
    # Serve the HTML file
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "index.html file not found", 404
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return f"Error loading page: {e}", 500

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
        
        # Validate required fields
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        # Validate email format
        email = data['email'].strip()
        if not email or '@' not in email:
            return jsonify({
                'success': False,
                'message': 'Please enter a valid email address'
            }), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Extract data with defaults
        name = data.get('name', '').strip()
        answers = data.get('answers', {})
        ministries = data.get('ministries', [])
        situation = data.get('situation', [])
        
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
            answers.get('state', ''),
            answers.get('interest', ''),
            json.dumps(situation),
            json.dumps(ministries),
            ip_address
        ))
        
        submission_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"Successfully saved submission {submission_id} for {email} from IP {ip_address}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for registering! Someone from St. Edward will be in touch soon.',
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
            
            # Handle JSONB fields
            if submission['situation']:
                if isinstance(submission['situation'], str):
                    submission['situation'] = json.loads(submission['situation'])
            
            if submission['recommended_ministries']:
                if isinstance(submission['recommended_ministries'], str):
                    submission['recommended_ministries'] = json.loads(submission['recommended_ministries'])
            
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
            .ministries, .situation { max-width: 150px; word-wrap: break-word; font-size: 10px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #005921; }
            .stat-number { font-size: 2em; font-weight: bold; color: #005921; }
            .export-btn { background: #005921; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 5px; }
            .export-btn:hover { background: #004a1e; }
            .recent { color: #e74c3c; font-weight: bold; }
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
                    .then(response => response.json())
                    .then(data => {
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
                    });
            }
            
            function convertToCSV(data) {
                const headers = ['Date', 'Name', 'Email', 'Age Group', 'Gender', 'State in Life', 'Interest', 'Situation', 'Recommended Ministries', 'IP Address'];
                let csv = headers.join(',') + '\\n';
                
                data.forEach(row => {
                    const situation = Array.isArray(row.situation) ? row.situation.join('; ') : '';
                    const ministries = Array.isArray(row.recommended_ministries) ? row.recommended_ministries.join('; ') : '';
                    const csvRow = [
                        new Date(row.submitted_at).toLocaleDateString(),
                        `"${row.name || ''}"`,
                        `"${row.email}"`,
                        `"${row.age_group || ''}"`,
                        `"${row.gender || ''}"`,
                        `"${row.state_in_life || ''}"`,
                        `"${row.interest || ''}"`,
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
                .then(response => response.json())
                .then(data => {
                    // Calculate stats
                    const totalSubmissions = data.length;
                    const uniqueEmails = new Set(data.map(s => s.email)).size;
                    const last24h = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 24*60*60*1000)).length;
                    const avgMinistries = data.reduce((sum, s) => sum + (s.recommended_ministries?.length || 0), 0) / totalSubmissions;
                    
                    // Show stats
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-number">${totalSubmissions}</div>
                            <div>Total Submissions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${uniqueEmails}</div>
                            <div>Unique Users</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${last24h}</div>
                            <div>Last 24 Hours</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${avgMinistries.toFixed(1)}</div>
                            <div>Avg Ministries per User</div>
                        </div>
                    `;
                    
                    // Show submissions table
                    let html = '<table><tr><th>Date</th><th>Name</th><th>Email</th><th>Age</th><th>Gender</th><th>State</th><th>Interest</th><th>Situation</th><th>Recommended Ministries</th><th>IP</th></tr>';
                    data.forEach(sub => {
                        const isRecent = new Date(sub.submitted_at) > new Date(Date.now() - 24*60*60*1000);
                        const situationText = Array.isArray(sub.situation) ? sub.situation.join(', ') : (sub.situation || '');
                        const ministriesText = Array.isArray(sub.recommended_ministries) ? sub.recommended_ministries.join(', ') : (sub.recommended_ministries || '');
                        
                        html += `<tr ${isRecent ? 'class="recent"' : ''}>
                            <td>${new Date(sub.submitted_at).toLocaleDateString()} ${new Date(sub.submitted_at).toLocaleTimeString()}</td>
                            <td>${sub.name || 'Not provided'}</td>
                            <td>${sub.email}</td>
                            <td>${sub.age_group || ''}</td>
                            <td>${sub.gender || ''}</td>
                            <td>${sub.state_in_life || ''}</td>
                            <td>${sub.interest || ''}</td>
                            <td class="situation">${situationText}</td>
                            <td class="ministries">${ministriesText}</td>
                            <td>${sub.ip_address || ''}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    document.getElementById('submissions').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('submissions').innerHTML = '<p style="color: red;">Error loading submissions: ' + error.message + '</p>';
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

if __name__ == '__main__':
    try:
        logger.info("Starting St. Edward Ministry Finder application")
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
