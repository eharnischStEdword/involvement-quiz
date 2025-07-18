# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import pytest
from app.validators import InputValidator, ValidationError, validate_and_respond

class TestInputValidator:
    """Test the InputValidator class"""
    
    def test_validate_age_group_valid(self):
        """Test valid age groups"""
        assert InputValidator.validate_age_group('25-35') == '25-35'
        assert InputValidator.validate_age_group('under-18') == 'under-18'
        assert InputValidator.validate_age_group('65-plus') == '65-plus'
        assert InputValidator.validate_age_group('') == ''
        assert InputValidator.validate_age_group(None) == ''
    
    def test_validate_age_group_invalid(self):
        """Test invalid age groups"""
        with pytest.raises(ValidationError):
            InputValidator.validate_age_group('invalid-age')
        
        with pytest.raises(ValidationError):
            InputValidator.validate_age_group('25')
    
    def test_validate_gender_valid(self):
        """Test valid genders"""
        assert InputValidator.validate_gender('male') == 'male'
        assert InputValidator.validate_gender('female') == 'female'
        assert InputValidator.validate_gender('other') == 'other'
        assert InputValidator.validate_gender('prefer-not-to-say') == 'prefer-not-to-say'
        assert InputValidator.validate_gender('') == ''
        assert InputValidator.validate_gender(None) == ''
    
    def test_validate_gender_invalid(self):
        """Test invalid genders"""
        with pytest.raises(ValidationError):
            InputValidator.validate_gender('invalid-gender')
    
    def test_validate_list_valid(self):
        """Test valid list validation"""
        valid_options = {'option1', 'option2', 'option3'}
        
        # Test empty list
        assert InputValidator.validate_list([], 'test', valid_options) == []
        
        # Test single item
        assert InputValidator.validate_list(['option1'], 'test', valid_options) == ['option1']
        
        # Test multiple items
        assert InputValidator.validate_list(['option1', 'option2'], 'test', valid_options) == ['option1', 'option2']
        
        # Test string conversion
        assert InputValidator.validate_list('option1', 'test', valid_options) == ['option1']
    
    def test_validate_list_invalid(self):
        """Test invalid list validation"""
        valid_options = {'option1', 'option2', 'option3'}
        
        # Test invalid option
        with pytest.raises(ValidationError):
            InputValidator.validate_list(['invalid'], 'test', valid_options)
        
        # Test too many items
        with pytest.raises(ValidationError):
            InputValidator.validate_list(['option1'] * 15, 'test', valid_options, max_items=10)
        
        # Test non-string item
        with pytest.raises(ValidationError):
            InputValidator.validate_list([123], 'test', valid_options)
    
    def test_validate_ministry_submission_valid(self, sample_submission_data):
        """Test valid ministry submission validation"""
        validated_data, errors = InputValidator.validate_ministry_submission(sample_submission_data)
        
        assert errors == []
        assert validated_data['age_group'] == '25-35'
        assert validated_data['gender'] == 'female'
        assert validated_data['states'] == ['single']
        assert validated_data['interests'] == ['music']
        assert validated_data['situation'] == ['new-to-parish']
        assert validated_data['ministries'] == ['mass', 'choir']
    
    def test_validate_ministry_submission_invalid(self, sample_invalid_submission_data):
        """Test invalid ministry submission validation"""
        validated_data, errors = InputValidator.validate_ministry_submission(sample_invalid_submission_data)
        
        assert len(errors) > 0
        assert any('age' in error for error in errors)
        assert any('gender' in error for error in errors)
    
    def test_validate_ministry_submission_missing_data(self):
        """Test validation with missing data"""
        data = {}
        validated_data, errors = InputValidator.validate_ministry_submission(data)
        
        assert errors == []
        assert validated_data['age_group'] == ''
        assert validated_data['gender'] == ''
        assert validated_data['states'] == []
        assert validated_data['interests'] == []
        assert validated_data['situation'] == []
        assert validated_data['ministries'] == []
    
    def test_validate_ministry_submission_too_many_ministries(self):
        """Test validation with too many ministries"""
        data = {
            'answers': {'age': '25-35', 'gender': 'female'},
            'ministries': ['ministry' + str(i) for i in range(25)],  # More than 20
            'situation': [],
            'states': [],
            'interests': []
        }
        
        validated_data, errors = InputValidator.validate_ministry_submission(data)
        
        assert len(errors) > 0
        assert any('ministries' in error for error in errors)

class TestValidateAndRespond:
    """Test the validate_and_respond function"""
    
    def test_validate_and_respond_valid(self, sample_submission_data):
        """Test valid data response"""
        validated_data, error_response = validate_and_respond(sample_submission_data)
        
        assert error_response is None
        assert validated_data is not None
        assert validated_data['age_group'] == '25-35'
    
    def test_validate_and_respond_invalid(self, sample_invalid_submission_data):
        """Test invalid data response"""
        validated_data, error_response = validate_and_respond(sample_invalid_submission_data)
        
        assert validated_data is None
        assert error_response is not None
        assert error_response[1] == 400  # HTTP status code
        
        # Check response structure
        response_data = error_response[0].json
        assert response_data['success'] is False
        assert 'errors' in response_data
    
    def test_validate_and_respond_empty_data(self):
        """Test response with empty data"""
        validated_data, error_response = validate_and_respond({})
        
        assert error_response is None
        assert validated_data is not None
        # Should return empty values for all fields
        assert validated_data['age_group'] == ''
        assert validated_data['gender'] == ''
        assert validated_data['states'] == []
        assert validated_data['interests'] == []
        assert validated_data['situation'] == []
        assert validated_data['ministries'] == [] 