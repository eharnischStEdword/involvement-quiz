import json
import logging
from app.database import get_db_connection

logger = logging.getLogger(__name__)

def load_ministries_from_db():
    """Load all active ministries from database"""
    ministries = {}
    
    try:
        with get_db_connection() as (conn, cur):
            cur.execute('''
                SELECT ministry_key, name, description, details, 
                       age_groups, genders, states, interests, situations
                FROM ministries 
                WHERE active = TRUE
                ORDER BY name
            ''')
            
            for row in cur.fetchall():
                key = row[0]
                ministries[key] = {
                    'name': row[1],
                    'description': row[2],
                    'details': row[3],
                    'age': json.loads(row[4]) if row[4] else [],
                    'gender': json.loads(row[5]) if row[5] else [],
                    'state': json.loads(row[6]) if row[6] else [],
                    'interest': json.loads(row[7]) if row[7] else [],
                    'situation': json.loads(row[8]) if row[8] else []
                }
        
        logger.info(f"Loaded {len(ministries)} ministries from database")
        return ministries
        
    except Exception as e:
        logger.error(f"Error loading ministries from database: {e}")
        # Fall back to hardcoded data if DB fails
        from app.ministries import MINISTRY_DATA
        return MINISTRY_DATA
