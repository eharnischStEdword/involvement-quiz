#!/usr/bin/env python3
"""
Simple script to check recent submissions in the database
"""

import sys
import os
# Add parent directory to path so app can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_connection
import psycopg2.extras
from datetime import datetime

def check_submissions():
    """Check recent submissions in the database"""
    try:
        with get_db_connection(cursor_factory=psycopg2.extras.RealDictCursor) as (conn, cur):
            # Get total count
            cur.execute('SELECT COUNT(*) as count FROM ministry_submissions')
            result = cur.fetchone()
            print(f"Total submissions in database: {result['count']}")
            
            # Get recent submissions
            cur.execute('''
                SELECT id, name, age_group, gender, state_in_life, interest, 
                       situation, recommended_ministries, submitted_at, ip_address
                FROM ministry_submissions
                ORDER BY submitted_at DESC
                LIMIT 10
            ''')
            
            recent = cur.fetchall()
            print(f"\nRecent submissions (last 10):")
            print("-" * 80)
            
            if not recent:
                print("No submissions found!")
                return
            
            for submission in recent:
                print(f"ID: {submission['id']}")
                print(f"Date: {submission['submitted_at']}")
                print(f"IP: {submission['ip_address']}")
                print(f"Age Group: {submission['age_group']}")
                print(f"Gender: {submission['gender']}")
                print(f"States: {submission['state_in_life']}")
                print(f"Interests: {submission['interest']}")
                print(f"Situations: {submission['situation']}")
                print(f"Ministries: {submission['recommended_ministries']}")
                print("-" * 40)
                
    except Exception as e:
        print(f"Error checking submissions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_submissions()
