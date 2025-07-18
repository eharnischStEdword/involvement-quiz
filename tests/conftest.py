# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Set up test environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['ADMIN_USERNAME'] = 'test_admin'
os.environ['ADMIN_PASSWORD'] = 'test_password'

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from main import app
    
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': None,  # Use in-memory database for tests
    })
    
    yield app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing."""
    with patch('app.database.get_db_connection') as mock:
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # Mock submission ID
        mock_cursor.fetchall.return_value = []
        
        # Set up the context manager
        mock.return_value.__enter__.return_value = (mock_conn, mock_cursor)
        mock.return_value.__exit__.return_value = None
        
        yield mock

@pytest.fixture
def sample_submission_data():
    """Sample valid submission data for testing."""
    return {
        'answers': {
            'age': '25-35',
            'gender': 'female'
        },
        'ministries': ['mass', 'choir'],
        'situation': ['new-to-parish'],
        'states': ['single'],
        'interests': ['music']
    }

@pytest.fixture
def sample_invalid_submission_data():
    """Sample invalid submission data for testing."""
    return {
        'answers': {
            'age': 'invalid-age',
            'gender': 'invalid-gender'
        },
        'ministries': ['invalid-ministry'],
        'situation': ['invalid-situation'],
        'states': ['invalid-state'],
        'interests': ['invalid-interest']
    } 