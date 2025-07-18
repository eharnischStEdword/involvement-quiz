# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import pytest
import json
from unittest.mock import patch

class TestAPISubmit:
    """Test the /api/submit endpoint"""
    
    def test_submit_valid_data(self, client, mock_db_connection, sample_submission_data):
        """Test submitting valid data"""
        response = client.post('/api/submit', 
                             json=sample_submission_data,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'submission_id' in data
        assert 'Thank you for exploring' in data['message']
    
    def test_submit_invalid_data(self, client, sample_invalid_submission_data):
        """Test submitting invalid data"""
        response = client.post('/api/submit', 
                             json=sample_invalid_submission_data,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'errors' in data
        assert len(data['errors']) > 0
    
    def test_submit_no_data(self, client):
        """Test submitting no data"""
        response = client.post('/api/submit', 
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'No data provided' in data['message']
    
    def test_submit_empty_json(self, client):
        """Test submitting empty JSON"""
        response = client.post('/api/submit', 
                             json={},
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200  # Empty data should be valid
        data = response.get_json()
        assert data['success'] is True
    
    def test_submit_database_error(self, client, sample_submission_data):
        """Test handling database errors"""
        with patch('app.database.get_db_connection') as mock_db:
            # Simulate database error
            mock_db.side_effect = Exception("Database connection failed")
            
            response = client.post('/api/submit', 
                                 json=sample_submission_data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False
            assert 'unexpected error' in data['message'].lower()
    
    def test_submit_rate_limit(self, client, sample_submission_data):
        """Test rate limiting"""
        with patch('app.utils.check_rate_limit') as mock_rate_limit:
            # Simulate rate limit exceeded
            mock_rate_limit.return_value = False
            
            response = client.post('/api/submit', 
                                 json=sample_submission_data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 429
            data = response.get_json()
            assert data['success'] is False
            assert 'too many submissions' in data['message'].lower()

class TestAPIHealth:
    """Test the /api/health endpoint"""
    
    def test_health_check_success(self, client, mock_db_connection):
        """Test successful health check"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'database' in data
        assert 'timestamp' in data
    
    def test_health_check_database_error(self, client):
        """Test health check with database error"""
        with patch('app.database.get_db_connection') as mock_db:
            # Simulate database error
            mock_db.side_effect = Exception("Database connection failed")
            
            response = client.get('/api/health')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['status'] == 'unhealthy'
            assert 'error' in data

class TestAPIGetMinistries:
    """Test the /api/get-ministries endpoint"""
    
    def test_get_ministries_success(self, client, mock_db_connection):
        """Test successful ministry retrieval"""
        # Mock the ministries data
        mock_cursor = mock_db_connection.return_value.__enter__.return_value[1]
        mock_cursor.fetchall.return_value = [
            {'ministry_key': 'mass', 'name': 'Come to Mass', 'active': True},
            {'ministry_key': 'choir', 'name': 'Choir', 'active': True}
        ]
        
        response = client.post('/api/get-ministries',
                             json={'test': 'data'},
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'mass' in data
        assert 'choir' in data
    
    def test_get_ministries_database_error(self, client):
        """Test ministry retrieval with database error"""
        with patch('app.database.get_db_connection') as mock_db:
            # Simulate database error
            mock_db.side_effect = Exception("Database connection failed")
            
            response = client.post('/api/get-ministries',
                                 json={'test': 'data'},
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data 