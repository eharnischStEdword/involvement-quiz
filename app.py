from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        # Local development
        conn = psycopg2.connect(
            host='localhost',
            database='st_edward_ministries',
            user='your_username',
            password='your_password'
        )
    return conn

# Initialize database
def init_db():
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
            recommended_ministries TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
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

@app.route('/')
def index():
    # Serve the HTML file
    with open('index.html', 'r') as f:
        html_content = f.read()
    return html_content

@app.route('/api/submit', methods=['POST'])
def submit_ministry_interest():
    try:
        data = request.json
        print(f"Received data: {data}")  # Debug logging
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO ministry_submissions 
            (name, email, age_group, gender, state_in_life, interest, recommended_ministries)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('name', ''),
            data['email'],
            data['answers'].get('age', ''),
            data['answers'].get('gender', ''),
            data['answers'].get('state', ''),
            data['answers'].get('interest', ''),
            json.dumps(data.get('ministries', []))
        ))
        
        submission_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Successfully saved submission {submission_id}")  # Debug logging
        
        # Here you would typically send an email to the parish office
        # and/or to the person who submitted
        
        return jsonify({
            'success': True,
            'message': 'Thank you! We\'ll send you more information about these ministries soon.',
            'submission_id': submission_id
        })
        
    except Exception as e:
        print(f"Error in submit_ministry_interest: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()  # Full error details
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}'  # Show actual error for debugging
        }), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Admin endpoint to view submissions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, name, email, age_group, gender, state_in_life, interest, 
                   recommended_ministries, submitted_at
            FROM ministry_submissions
            ORDER BY submitted_at DESC
        ''')
        
        submissions = []
        for row in cur.fetchall():
            submissions.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'age_group': row[3],
                'gender': row[4],
                'state_in_life': row[5],
                'interest': row[6],
                'recommended_ministries': json.loads(row[7]) if row[7] else [],
                'submitted_at': row[8].isoformat() if row[8] else None
            })
        
        cur.close()
        conn.close()
        
        return jsonify(submissions)
        
    except Exception as e:
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
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .ministries { max-width: 200px; word-wrap: break-word; }
        </style>
    </head>
    <body>
        <h1>St. Edward Ministry Finder Submissions</h1>
        <div id="submissions"></div>
        
        <script>
            fetch('/api/submissions')
                .then(response => response.json())
                .then(data => {
                    let html = '<table><tr><th>Date</th><th>Name</th><th>Email</th><th>Age</th><th>Gender</th><th>State</th><th>Interest</th><th>Recommended Ministries</th></tr>';
                    data.forEach(sub => {
                        html += `<tr>
                            <td>${new Date(sub.submitted_at).toLocaleDateString()}</td>
                            <td>${sub.name || 'Not provided'}</td>
                            <td>${sub.email}</td>
                            <td>${sub.age_group}</td>
                            <td>${sub.gender}</td>
                            <td>${sub.state_in_life}</td>
                            <td>${sub.interest}</td>
                            <td class="ministries">${sub.recommended_ministries.join(', ')}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    document.getElementById('submissions').innerHTML = html;
                });
        </script>
    </body>
    </html>
    '''
    return admin_html

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
