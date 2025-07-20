# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from flask import jsonify

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class InputValidator:
    """Simple input validation class"""
    
    # Valid age groups
    VALID_AGE_GROUPS = {
        'infant', 'elementary', 'junior-high', 'high-school', 'college-young-adult', 'married-parents', 'journeying-adults'
    }
    
    # Valid genders
    VALID_GENDERS = {
        'male', 'female', 'other', 'prefer-not-to-say'
    }
    
    # Valid states in life
    VALID_STATES = {
        'single', 'married', 'parent', 'none-of-above'
    }
    
    # Valid interests
    VALID_INTERESTS = {
        'fellowship', 'service', 'education', 'prayer', 'music', 'support', 'kids', 'all'
    }
    
    # Valid situations
    VALID_SITUATIONS = {
        'new-to-stedward', 'returning-to-church', 'new-to-nashville', 'current-parishioner', 'just-curious', 'situation-none-of-above'
    }
    
    @staticmethod
    def validate_string(value: Any, field_name: str, max_length: int = 255, required: bool = True) -> str:
        """Validate a string field"""
        if required and (value is None or value == ''):
            raise ValidationError(f"{field_name} is required", field_name)
        
        if value is None:
            return ''
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string", field_name)
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must be {max_length} characters or less", field_name)
        
        # Remove any potentially dangerous characters
        cleaned = re.sub(r'[<>"\']', '', value.strip())
        return cleaned
    
    @staticmethod
    def validate_email(email: Any, required: bool = False) -> str:
        """Validate email format"""
        if not required and (email is None or email == ''):
            return ''
        
        if not isinstance(email, str):
            raise ValidationError("Email must be a string", "email")
        
        email = email.strip().lower()
        
        # Simple email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format", "email")
        
        if len(email) > 255:
            raise ValidationError("Email must be 255 characters or less", "email")
        
        return email
    
    @staticmethod
    def validate_age_group(age: Any) -> str:
        """Validate age group"""
        if not age:
            return ''
        
        age = str(age).lower().strip()
        if age not in InputValidator.VALID_AGE_GROUPS:
            raise ValidationError(f"Invalid age group. Must be one of: {', '.join(InputValidator.VALID_AGE_GROUPS)}", "age")
        
        return age
    
    @staticmethod
    def validate_gender(gender: Any) -> str:
        """Validate gender"""
        if not gender:
            return ''
        
        gender = str(gender).lower().strip()
        if gender not in InputValidator.VALID_GENDERS:
            raise ValidationError(f"Invalid gender. Must be one of: {', '.join(InputValidator.VALID_GENDERS)}", "gender")
        
        return gender
    
    @staticmethod
    def validate_list(values: Any, field_name: str, valid_options: set, max_items: int = 10) -> List[str]:
        """Validate a list of values"""
        if not values:
            return []
        
        if not isinstance(values, list):
            # Try to convert string to list
            if isinstance(values, str):
                values = [values]
            else:
                raise ValidationError(f"{field_name} must be a list", field_name)
        
        if len(values) > max_items:
            raise ValidationError(f"{field_name} cannot have more than {max_items} items", field_name)
        
        validated = []
        for value in values:
            if not isinstance(value, str):
                raise ValidationError(f"All items in {field_name} must be strings", field_name)
            
            value = value.lower().strip()
            if value not in valid_options:
                raise ValidationError(f"Invalid {field_name}: {value}. Must be one of: {', '.join(valid_options)}", field_name)
            
            validated.append(value)
        
        return validated
    
    @staticmethod
    def validate_ministry_submission(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Validate a complete ministry submission"""
        errors = []
        validated_data = {}
        
        try:
            # Validate answers
            answers = data.get('answers', {})
            if not isinstance(answers, dict):
                raise ValidationError("Answers must be an object", "answers")
            
            validated_data['age_group'] = InputValidator.validate_age_group(answers.get('age'))
            validated_data['gender'] = InputValidator.validate_gender(answers.get('gender'))
            
            # Validate lists
            validated_data['states'] = InputValidator.validate_list(
                data.get('states', []), 
                'states', 
                InputValidator.VALID_STATES
            )
            
            validated_data['interests'] = InputValidator.validate_list(
                data.get('interests', []), 
                'interests', 
                InputValidator.VALID_INTERESTS
            )
            
            validated_data['situation'] = InputValidator.validate_list(
                data.get('situation', []), 
                'situation', 
                InputValidator.VALID_SITUATIONS
            )
            
            # Validate ministries (must be list of strings)
            ministries = data.get('ministries', [])
            if not isinstance(ministries, list):
                raise ValidationError("Ministries must be a list", "ministries")
            
            if len(ministries) > 20:  # Reasonable limit
                raise ValidationError("Too many ministries selected", "ministries")
            
            validated_ministries = []
            for ministry in ministries:
                if not isinstance(ministry, str):
                    raise ValidationError("All ministries must be strings", "ministries")
                ministry = ministry.strip()
                if len(ministry) > 100:  # Reasonable limit
                    raise ValidationError("Ministry name too long", "ministries")
                validated_ministries.append(ministry)
            
            validated_data['ministries'] = validated_ministries
            
        except ValidationError as e:
            errors.append(f"{e.field}: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            errors.append("Unexpected validation error")
        
        return validated_data, errors

def validate_and_respond(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple]]:
    """
    Validate submission data and return appropriate response
    
    Returns:
        Tuple of (validated_data, error_response)
        If validation fails, validated_data is None and error_response is a Flask response
        If validation succeeds, error_response is None
    """
    try:
        validated_data, errors = InputValidator.validate_ministry_submission(data)
        
        if errors:
            return None, (jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400)
        
        return validated_data, None
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return None, (jsonify({
            'success': False,
            'message': 'Validation error occurred'
        }), 400) 