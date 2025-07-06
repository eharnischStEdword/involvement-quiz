from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from datetime import datetime
import json
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Initialize database
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
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add situation column if it doesn't exist (for existing databases)
        cur.execute('''
            DO $ 
            BEGIN 
                BEGIN
                    ALTER TABLE ministry_submissions ADD COLUMN situation JSONB DEFAULT '[]'::jsonb;
                EXCEPTION
                    WHEN duplicate_column THEN null;
                END;
            END $;
        ''')
        
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
        data = request.json
        logger.info(f"Received submission data: {data}")
        
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
            (name, email, age_group, gender, state_in_life, interest, situation, recommended_ministries)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            name,
            email,
            answers.get('age', ''),
            answers.get('gender', ''),
            answers.get('state', ''),
            answers.get('interest', ''),
            json.dumps(situation),
            json.dumps(ministries)
        ))
        
        submission_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"Successfully saved submission {submission_id} for {email}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you! We\'ll send you more information about these ministries soon.',
            'submission_id': submission_id
        })
        
    except psycopg2.Error as e:
        logger.error(f"Database error in submit_ministry_interest: {e}")
        return jsonify({
            'success': False,
            'message': f'Database error: Please try again or contact the parish office at (615) 833-5520'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in submit_ministry_interest: {e}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again or contact the parish office.'
        }), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Admin endpoint to view submissions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute('''
            SELECT id, name, email, age_group, gender, state_in_life, interest, 
                   situation, recommended_ministries, submitted_at
            FROM ministry_submissions
            ORDER BY submitted_at DESC
        ''')
        
        submissions = []
        for row in cur.fetchall():
            submission = dict(row)
            # Parse JSON fields
            if submission['situation']:
                submission['situation'] = json.loads(submission['situation'])
            if submission['recommended_ministries']:
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
def admin_dashboard():
    """Simple admin page to view submissions"""
    admin_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>St. Edward Ministry Submissions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            h1 { color: #005921; text-align: center; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }
            th { background-color: #005921; color: white; }
            .ministries, .situation { max-width: 200px; word-wrap: break-word; font-size: 12px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #005921; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>St. Edward Ministry Finder Submissions</h1>
            <div class="stats" id="stats"></div>
            <div id="submissions"></div>
        </div>
        
        <script>
            fetch('/api/submissions')
                .then(response => response.json())
                .then(data => {
                    // Calculate stats
                    const totalSubmissions = data.length;
                    const uniqueEmails = new Set(data.map(s => s.email)).size;
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
                            <div class="stat-number">${avgMinistries.toFixed(1)}</div>
                            <div>Avg Ministries per User</div>
                        </div>
                    `;
                    
                    // Show submissions table
                    let html = '<table><tr><th>Date</th><th>Name</th><th>Email</th><th>Age</th><th>Gender</th><th>State</th><th>Interest</th><th>Situation</th><th>Recommended Ministries</th></tr>';
                    data.forEach(sub => {
                        const situationText = Array.isArray(sub.situation) ? sub.situation.join(', ') : (sub.situation || '');
                        const ministriesText = Array.isArray(sub.recommended_ministries) ? sub.recommended_ministries.join(', ') : (sub.recommended_ministries || '');
                        
                        html += `<tr>
                            <td>${new Date(sub.submitted_at).toLocaleDateString()}</td>
                            <td>${sub.name || 'Not provided'}</td>
                            <td>${sub.email}</td>
                            <td>${sub.age_group || ''}</td>
                            <td>${sub.gender || ''}</td>
                            <td>${sub.state_in_life || ''}</td>
                            <td>${sub.interest || ''}</td>
                            <td class="situation">${situationText}</td>
                            <td class="ministries">${ministriesText}</td>
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
        init_db()
        logger.info("Starting St. Edward Ministry Finder application")
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
