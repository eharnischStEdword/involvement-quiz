#!/usr/bin/env python3
"""
Test script to simulate a quiz submission
"""

import requests
import json
import sys

def test_quiz_submission():
    """Test the quiz submission API"""
    
    # Test data - simulating an infant taking the quiz
    test_data = {
        "answers": {
            "age": "infant",
            "gender": "male"
        },
        "states": ["single"],  # Auto-assigned for infants
        "interests": ["kids"],  # Age-appropriate interests for infants
        "situation": ["new-to-stedward"],
        "ministries": ["infant-baptism", "prep-kids"]
    }
    
    # Try to submit to the production URL
    url = "https://involvement-quiz.onrender.com/api/submit"
    
    print(f"Testing quiz submission to: {url}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Submission ID: {result.get('submission_id')}")
            print(f"Message: {result.get('message')}")
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def test_admin_access():
    """Test admin dashboard access"""
    
    url = "https://involvement-quiz.onrender.com/admin/api/submissions"
    
    print(f"\nTesting admin API access: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Admin API response status: {response.status_code}")
        
        if response.status_code == 401:
            print("Admin API requires authentication (expected)")
        elif response.status_code == 200:
            data = response.json()
            print(f"Admin API accessible! Found {len(data)} submissions")
        else:
            print(f"Unexpected response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Admin API request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    print("=== Quiz Submission Test ===\n")
    test_quiz_submission()
    test_admin_access()
