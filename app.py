from flask import Flask, request, jsonify, render_template
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
        
        # Create submissions table with updated schema
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ministry_submissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) NOT NULL,
                age_group VARCHAR(50),
                gender VARCHAR(20),
                state_in_life JSONB DEFAULT '[]'::jsonb,
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
        
        # SAFE MIGRATION: Update state_in_life column to be JSONB if it's not already
        cur.execute("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'state_in_life'
        """)
        result = cur.fetchone()
        if result and result[0] != 'jsonb':
            logger.info("Converting state_in_life column to JSONB...")
            
            # Safe conversion: wrap existing string values in JSON arrays
            try:
                # First, handle NULL values
                cur.execute("""
                    UPDATE ministry_submissions 
                    SET state_in_life = '[]'::jsonb 
                    WHERE state_in_life IS NULL OR state_in_life = ''
                """)
                
                # Then convert non-empty string values to JSON arrays
                cur.execute("""
                    UPDATE ministry_submissions 
                    SET state_in_life = ('["' || state_in_life || '"]')::jsonb 
                    WHERE state_in_life IS NOT NULL 
                    AND state_in_life != '' 
                    AND state_in_life !~ '^\\[.*\\]$'
                """)
                
                # Now safely convert the column type
                cur.execute("""
                    ALTER TABLE ministry_submissions 
                    ALTER COLUMN state_in_life TYPE JSONB 
                    USING COALESCE(state_in_life::jsonb, '[]'::jsonb)
                """)
                
                logger.info("Successfully updated state_in_life column to JSONB type")
                
            except Exception as e:
                logger.error(f"Error converting state_in_life to JSONB: {e}")
                # If conversion fails, just ensure the column exists as VARCHAR for now
                logger.info("Keeping state_in_life as VARCHAR for now - will work with existing data")
        
        # SAFE MIGRATION: Handle interest column similarly if needed
        cur.execute("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'ministry_submissions' AND column_name = 'interest'
        """)
        result = cur.fetchone()
        if result and result[0] == 'character varying':
            logger.info("Interest column is VARCHAR - this is fine for backward compatibility")
        
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
        # Don't raise the exception - let the app continue
        logger.info("Continuing with existing database schema")

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
    # Serve the template with proper Flask template rendering
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
            
            # Handle JSONB fields
            if submission['situation']:
                if isinstance(submission['situation'], str):
                    submission['situation'] = json.loads(submission['situation'])
            
            if submission['state_in_life']:
                if isinstance(submission['state_in_life'], str):
                    submission['state_in_life'] = json.loads(submission['state_in_life'])
            
            if submission['interest']:
                if isinstance(submission['interest'], str):
                    submission['interest'] = json.loads(submission['interest'])
            
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
            .ministries, .situation, .states, .interests { max-width: 150px; word-wrap: break-word; font-size: 10px; }
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
                const headers = ['Date', 'Name', 'Email', 'Age Group', 'Gender', 'States', 'Interests', 'Situation', 'Recommended Ministries', 'IP Address'];
                let csv = headers.join(',') + '\\n';
                
                data.forEach(row => {
                    const situation = Array.isArray(row.situation) ? row.situation.join('; ') : '';
                    const states = Array.isArray(row.state_in_life) ? row.state_in_life.join('; ') : '';
                    const interests = Array.isArray(row.interest) ? row.interest.join('; ') : '';
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
                .then(response => response.json())
                .then(data => {
                    // Calculate stats
                    const totalSubmissions = data.length;
                    const last24h = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 24*60*60*1000)).length;
                    const avgMinistries = data.reduce((sum, s) => sum + (s.recommended_ministries?.length || 0), 0) / totalSubmissions;
                    
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
                            <div class="stat-number">${avgMinistries.toFixed(1)}</div>
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

# ===== ADD EVERYTHING BELOW THIS LINE TO YOUR APP.PY =====

# Ministry data (moved from JavaScript for protection)
MINISTRY_DATA = {
    # Sacraments
    'mass': {
        'name': 'Come to Mass!',
        'description': 'The source and summit of our faith.',
        'details': 'Daily & Weekend Mass times are available at <a href="https://stedward.org" target="_blank">stedward.org</a>',
        'age': ['infant', 'kid', 'junior-high', 'high-school', 'college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['prayer', 'all']
    }
    'confession': {
        'name': 'Sacrament of Confession',
        'description': 'Reconciliation and spiritual healing',
        'details': 'Confession times available at <a href="https://stedward.org" target="_blank">stedward.org</a>',
        'age': ['kid', 'junior-high', 'high-school', 'college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['prayer', 'all']
    },
    'ocia': {
        'name': 'OCIA (Adult Baptism/Full Communion)',
        'description': 'Program that prepares adults for Baptism, Holy Communion & Confirmation',
        'details': 'Visit <a href="https://stedward.org/ocia" target="_blank">stedward.org/ocia</a> for more information',
        'age': ['college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['education', 'prayer']
    },
    'infant-baptism': {
        'name': 'Infant Baptism (0-5 yrs)',
        'description': 'Baptism preparation for families with young children',
        'details': 'Visit <a href="https://stedward.org/baptism" target="_blank">stedward.org/baptism</a> to register',
        'age': ['infant'],
        'interest': ['education', 'prayer', 'all']
    },
    'marriage-convalidation': {
        'name': 'Marriage Convalidation',
        'description': 'Sacrament of Holy Matrimony for civilly married couples',
        'details': 'Fill out intake form at <a href="https://stedward.org/marriage-prep" target="_blank">stedward.org/marriage-prep</a>',
        'age': ['college-young-adult', 'married-parents'],
        'state': ['married'],
        'interest': ['education', 'prayer']
    },
    
    # Welcome & New Member Support
    'welcome-committee': {
        'name': 'Welcome to St. Edward!',
        'description': 'New parishioner orientation and support',
        'details': 'Register online: <a href="https://stedwardnash.flocknote.com/register" target="_blank">stedwardnash.flocknote.com/register</a><br>Follow us: <a href="https://www.instagram.com/stedwardcommunity/" target="_blank">Instagram</a> | <a href="https://www.facebook.com/stedwardschool" target="_blank">Facebook</a><br>Photo galleries: <a href="https://stedward.smugmug.com/" target="_blank">stedward.smugmug.com</a>',
        'age': ['college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['fellowship', 'all'],
        'situation': ['new-to-stedward']
    },
    'returning-catholic': {
        'name': "If It's Been A While...",
        'description': "Welcome! We're happy you're here!",
        'details': 'Call (615) 833-5520 or email <a href="mailto:support@stedward.org">support@stedward.org</a>',
        'age': ['college-young-adult', 'married-parents', 'journeying-adults'],
        'interest': ['prayer', 'education', 'all'],
        'situation': ['returning-to-church']
    },
    
    # Knights of Columbus (by age group)
    'knights-ya': {
        'name': 'Knights of Columbus',
        'description': "Catholic men's fraternal organization - Focus on charity, unity, fraternity, and patriotism",
        'details': 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> for more information',
        'age': ['college-young-adult'],
        'gender': ['male'],
        'interest': ['fellowship', 'service', 'prayer']
    },
    'knights-parents': {
        'name': 'Knights of Columbus',
        'description': "Catholic men's fraternal organization - Service fraternity with monthly Cor Nights and insurance benefits",
        'details': 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> for more information',
        'age': ['married-parents'],
        'gender': ['male'],
        'interest': ['fellowship', 'service']
    },
    'knights-adults': {
        'name': 'Knights of Columbus',
        'description': "Catholic men's fraternal organization - Full benefits including insurance and financial planning",
        'details': 'Visit <a href="https://stedward.org/kofc" target="_blank">stedward.org/kofc</a> to become a St. Edward Knight',
        'age': ['journeying-adults'],
        'gender': ['male'],
        'interest': ['fellowship', 'service']
    },
    
    # Ladies Auxiliary (by age group)
    'ladies-aux-ya': {
        'name': 'Ladies Auxiliary',
        'description': "Women's fellowship and service - Prayer, service, fellowship for women",
        'details': 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        'age': ['college-young-adult'],
        'gender': ['female'],
        'interest': ['fellowship', 'service', 'prayer']
    },
    'ladies-aux-parents': {
        'name': 'Ladies Auxiliary',
        'description': "Women's fellowship and service - Service, crafts, Angel-Tree outreach",
        'details': 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        'age': ['married-parents'],
        'gender': ['female'],
        'interest': ['fellowship', 'service']
    },
    'ladies-aux-adults': {
        'name': 'Ladies Auxiliary',
        'description': "Women's fellowship and service",
        'details': 'Visit <a href="https://stedward.org/ladies-auxiliary" target="_blank">stedward.org/ladies-auxiliary</a> for information',
        'age': ['journeying-adults'],
        'gender': ['female'],
        'interest': ['fellowship', 'service']
    },
    
    # Sacred Music/Choir (by age group)
    'choir-hs': {
        'name': 'Sacred Music / Choir',
        'description': 'Weekly rehearsal & Mass service (Age 16+)',
        'details': 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        'age': ['high-school'],
        'interest': ['music', 'prayer']
    },
    'choir-ya': {
        'name': 'Sacred Music / Choir',
        'description': 'Weekly rehearsal & Mass service',
        'details': 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        'age': ['college-young-adult'],
        'interest': ['music', 'prayer']
    },
    'choir-adults': {
        'name': 'Sacred Music / Choir',
        'description': 'Weekly rehearsal & Mass service',
        'details': 'Fill out form: <a href="https://forms.office.com/Pages/ResponsePage.aspx?id=spbPjOu3C0enFewWltg-vSGAojmE4WpCvxL72BS8279UN0RYT042M0dDNlNLQ0ZTSDlFQ1ZWMTdKWC4u" target="_blank">Sacred Music Interest Form</a><br>Or contact <a href="mailto:nrankin@stedward.org">nrankin@stedward.org</a>',
        'age': ['journeying-adults'],
        'interest': ['music', 'prayer']
    },
    
    # Fraternus (by age group)
    'fraternus-jr': {
        'name': 'Fraternus',
        'description': 'Brotherhood & virtue formation - Weekly meetings and excursions developing Catholic men',
        'details': 'Wednesdays 6:00-8:00pm. Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        'age': ['junior-high'],
        'gender': ['male'],
        'interest': ['fellowship', 'education']
    },
    'fraternus-hs': {
        'name': 'Fraternus',
        'description': 'Brotherhood & virtue formation - Weekly formation, excursions, and retreats developing virtuous Catholic men',
        'details': 'Wednesdays 6:00-8:00pm with 4 weekend excursions. Contact <a href="mailto:support@stedward.org">support@stedward.org</a>',
        'age': ['high-school'],
        'gender': ['male'],
        'interest': ['fellowship', 'education']
    },
    'fraternus-mentors': {
        'name': 'Fraternus Adult Mentors',
        'description': 'College men serve younger boys (Wednesday evenings)',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        'age': ['college-young-adult'],
        'gender': ['male'],
        'interest': ['service', 'fellowship']
    },
    
    # Fidelis (by age group)
    'fidelis-jr': {
        'name': 'Fidelis',
        'description': 'Sisterhood & virtue formation - Faith-filled friendships through discussion, activities, and fun',
        'details': 'Bi-weekly Wednesdays 6:30-8:30pm. Contact <a href="mailto:fidelisnashville@gmail.com">fidelisnashville@gmail.com</a>',
        'age': ['junior-high'],
        'gender': ['female'],
        'interest': ['fellowship', 'education']
    },
    'fidelis-hs': {
        'name': 'Fidelis',
        'description': 'Sisterhood & virtue formation - Weekly formation, excursions, and retreats for young women in faith',
        'details': 'Bi-weekly Wednesdays 6:30-8:30pm. Contact <a href="mailto:fidelisnashville@gmail.com">fidelisnashville@gmail.com</a>',
        'age': ['high-school'],
        'gender': ['female'],
        'interest': ['fellowship', 'education']
    },
    
    # Totus Tuus (by age group)
    'totus-tuus-kids': {
        'name': 'Totus Tuus Summer Program (Grades 1-6)',
        'description': 'Week-long summer catechetical program with games and activities',
        'details': 'Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        'age': ['kid'],
        'interest': ['education', 'fellowship', 'prayer']
    },
    'totus-tuus-jr': {
        'name': 'Totus Tuus Summer Program',
        'description': 'Summer catechetical program with peer ministry opportunities',
        'details': 'Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        'age': ['junior-high'],
        'interest': ['education', 'fellowship', 'prayer']
    },
    'totus-tuus-hs': {
        'name': 'Totus Tuus Summer Program',
        'description': 'Apologetics & fellowship for high schoolers with leadership opportunities',
        'details': 'Visit <a href="https://stedward.org/totus-tuus" target="_blank">stedward.org/totus-tuus</a> - registration opens in spring',
        'age': ['high-school'],
        'interest': ['education', 'fellowship', 'prayer']
    },
    'totus-tuus-missionary': {
        'name': 'Totus Tuus Missionary Teams',
        'description': 'Summer evangelization work teaching children and teens',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for application',
        'age': ['college-young-adult'],
        'interest': ['service', 'education', 'prayer']
    },
    
    # PREP (by age group)
    'prep-kids': {
        'name': 'PREP - Sunday Religious Ed',
        'description': 'Faith formation including First Confession & First Holy Communion prep',
        'details': 'Visit <a href="https://stedward.org/prep" target="_blank">stedward.org/prep</a> to register',
        'age': ['kid'],
        'interest': ['education', 'prayer']
    },
    'prep-jr': {
        'name': 'PREP - Sacrament Prep & Faith Formation',
        'description': 'Religious education and sacrament preparation',
        'details': 'Visit <a href="https://stedward.org/prep" target="_blank">stedward.org/prep</a> to register',
        'age': ['junior-high'],
        'interest': ['education', 'prayer']
    },
    
    # Coffee & Donuts (by age group)
    'coffee-donuts-parents': {
        'name': 'Coffee & Donuts Hospitality Team',
        'description': 'Once a month after-Mass fellowship in Little Carrel Room - Grab a treat for the ride home!',
        'details': 'Just stop on by! Interested in helping out? Visit <a href="https://stedward.org/coffee-donuts" target="_blank">stedward.org/coffee-donuts</a> to volunteer',
        'age': ['married-parents'],
        'interest': ['fellowship', 'service']
    },
    'coffee-donuts-adults': {
        'name': 'Coffee & Donuts Hospitality Team',
        'description': 'Once a month after-Mass fellowship in Little Carrel Room',
        'details': 'Just stop on by! Interested in helping out? Visit <a href="https://stedward.org/coffee-donuts" target="_blank">stedward.org/coffee-donuts</a> to volunteer',
        'age': ['journeying-adults'],
        'interest': ['fellowship', 'service']
    },
    
    # Bereavement Ministry (by age group)
    'bereavement-parents': {
        'name': 'Bereavement Meal Ministry',
        'description': 'Support families - Cook/serve funeral-day luncheons',
        'details': 'Visit <a href="https://stedward.org/bereavement" target="_blank">stedward.org/bereavement</a> to find out more',
        'age': ['married-parents'],
        'interest': ['service']
    },
    'bereavement-adults': {
        'name': 'Bereavement Meal Ministry',
        'description': 'Support families during difficult times by cooking and serving funeral luncheons',
        'details': 'Visit <a href="https://stedward.org/bereavement" target="_blank">stedward.org/bereavement</a> to find out more',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    
    # St. Vincent de Paul (by age group)
    'svdp-parents': {
        'name': 'St. Vincent de Paul Society',
        'description': 'Helping neighbors in need - Support for neighbors in need, meet first Sunday monthly',
        'details': 'Call Rick Prickett (615) 283-0374 or visit <a href="https://stedward.org/st-vincent-de-paul" target="_blank">stedward.org/st-vincent-de-paul</a>',
        'age': ['married-parents'],
        'interest': ['service']
    },
    'svdp-adults': {
        'name': 'St. Vincent de Paul Society',
        'description': 'Helping neighbors in need - Meet first Sunday monthly in Scout Room',
        'details': 'Call Rick Prickett (615) 283-0374 or visit <a href="https://stedward.org/st-vincent-de-paul" target="_blank">stedward.org/st-vincent-de-paul</a>',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    
    # Parent Support
    'moms-group': {
        'name': 'Moms Group',
        'description': 'Spiritual & practical support for mothers with rosary walks and monthly brunch',
        'details': 'Join on Flocknote: <a href="https://stedwardnash.flocknote.com/signup/180620" target="_blank">stedwardnash.flocknote.com/signup/180620</a><br>Or join GroupMe: <a href="https://groupme.com/join_group/107457911/mdAevstX" target="_blank">groupme.com/join_group/107457911/mdAevstX</a>',
        'age': ['infant', 'married-parents'],
        'gender': ['female'],
        'state': ['parent'],
        'interest': ['fellowship', 'support', 'prayer']
    },
    'meal-train-receive': {
        'name': 'Meal Train Support for Your Family',
        'description': 'We want to serve you and support you with our meal train for families with new members!',
        'details': 'Contact <a href="mailto:elizabethlansden@gmail.com">elizabethlansden@gmail.com</a> if your family is growing soon and would like to receive meals',
        'age': ['infant'],
        'interest': ['support', 'fellowship', 'all']
    },
    'meal-train-provide': {
        'name': 'Meal Train for New Families',
        'description': 'Support growing families with meal delivery when they welcome a baby, adopt, or receive a foster child',
        'details': 'Flexible commitment - participate 1-3 times per year. Contact <a href="mailto:elizabethlansden@gmail.com">elizabethlansden@gmail.com</a> to join the volunteer list',
        'age': ['married-parents', 'college-young-adult', 'journeying-adults'],
        'interest': ['service', 'fellowship', 'support']
    },
    
    # Kids Programs
    'st-edward-school': {
        'name': 'St. Edward School (PreK-8th Grade)',
        'description': 'Catholic education in a faith-filled community environment',
        'details': 'Apply for enrollment: <a href="https://ses.stedward.org/apply" target="_blank">ses.stedward.org/apply</a>',
        'age': ['kid'],
        'interest': ['education', 'fellowship', 'all']
    },
    'cub-scouts': {
        'name': 'Cub Scouts',
        'description': 'Character development and outdoor adventures for boys and girls',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for more information',
        'age': ['kid'],
        'interest': ['fellowship', 'service', 'all']
    },
    'catechesis': {
        'name': 'Catechesis of the Good Shepherd Atrium',
        'description': 'Montessori-based religious education for Pre-K-2',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for enrollment',
        'age': ['kid'],
        'interest': ['education', 'prayer']
    },
    
    # High School Liturgical
    'liturgical-hs': {
        'name': 'Liturgical Ministries (Age 16+)',
        'description': 'Serve as lector, hospitality, or EMHC',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for training',
        'age': ['high-school'],
        'interest': ['service', 'prayer']
    },
    
    # Young Adult Programs
    'theology-tap': {
        'name': 'Theology on Tap (Summer Series)',
        'description': 'Faith & fellowship in beer-garden setting with engaging speakers',
        'details': 'Visit <a href="https://stedward.org/theo-on-tap" target="_blank">stedward.org/theo-on-tap</a> - check bulletin for dates',
        'age': ['college-young-adult'],
        'interest': ['fellowship', 'education']
    },
    'ocia-sponsors': {
        'name': 'OCIA Sponsors',
        'description': 'Accompany adults entering the Church',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        'age': ['college-young-adult'],
        'interest': ['service', 'education']
    },
    'room-inn-ya': {
        'name': 'Room-in-the-Inn Shelter Crew',
        'description': 'Saturday-night hospitality for homeless men during winter months',
        'details': 'Contact Greg Beem at <a href="mailto:support@stedward.org">support@stedward.org</a>',
        'age': ['college-young-adult'],
        'interest': ['service']
    },
    'cursillo': {
        'name': 'Cursillo Retreats',
        'description': 'Three-day renewal weekends focused on spiritual growth',
        'details': 'Visit <a href="https://stedward.org/cursillo" target="_blank">stedward.org/cursillo</a> for information',
        'age': ['college-young-adult'],
        'interest': ['prayer', 'fellowship']
    },
    
    # Marriage & Family
    'marriage-enrichment': {
        'name': 'Marriage Enrichment Nights',
        'description': 'Strengthen your marriage through faith',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for schedule',
        'age': ['married-parents'],
        'state': ['married'],
        'interest': ['fellowship', 'education', 'support']
    },
    
    # Adult Ministries
    'hospitality-ministry': {
        'name': 'Hospitality Ministry',
        'description': 'Welcome and serve parish community',
        'details': 'Visit <a href="https://stedward.org/hospitality-ministry" target="_blank">stedward.org/hospitality-ministry</a> for information',
        'age': ['journeying-adults'],
        'interest': ['fellowship', 'service']
    },
    'adoration-guild': {
        'name': 'Adoration Guild',
        'description': 'Committed prayer before the Blessed Sacrament',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        'age': ['journeying-adults'],
        'interest': ['prayer']
    },
    'catechists': {
        'name': 'Catechists',
        'description': 'Teach faith formation classes',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        'age': ['journeying-adults'],
        'interest': ['education', 'service']
    },
    'liturgical-adults': {
        'name': 'Serving at Mass',
        'description': 'Lector, EMHC, Usher',
        'details': 'Visit <a href="https://stedward.org/liturgical" target="_blank">stedward.org/liturgical</a> for training',
        'age': ['journeying-adults'],
        'interest': ['prayer', 'service']
    },
    'room-inn-adults': {
        'name': 'Room In The Inn',
        'description': 'Service & hospitality for homeless men during winter months',
        'details': 'Visit <a href="https://stedward.org/room-in-the-inn" target="_blank">stedward.org/room-in-the-inn</a> or contact Greg Beem',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    'haiti-sister-parish': {
        'name': 'Haiti Sister Parish Support',
        'description': 'Support our sister parish in Haiti',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        'age': ['journeying-adults'],
        'interest': ['service']
    },
    'bible-bunco': {
        'name': 'Bible Bunco & Blessings',
        'description': 'Faith and fellowship through games',
        'details': 'Contact <a href="mailto:support@stedward.org">support@stedward.org</a> for information',
        'age': ['journeying-adults'],
        'gender': ['female'],
        'interest': ['fellowship', 'education']
    }
}

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

if __name__ == '__main__':
    try:
        logger.info("Starting St. Edward Ministry Finder application")
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
