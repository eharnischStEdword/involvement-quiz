#!/usr/bin/env python3
# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

"""
Simple test runner for the St. Edward Ministry Finder application.
This script sets up the proper environment and runs the tests.
"""

import os
import sys
import subprocess

def setup_test_environment():
    """Set up the test environment variables"""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
    os.environ['ADMIN_USERNAME'] = 'test_admin'
    os.environ['ADMIN_PASSWORD'] = 'test_password'
    os.environ['DATABASE_URL'] = ''  # Force development mode
    
    print("✅ Test environment configured")

def run_validation_tests():
    """Run just the validation tests (these should work without database)"""
    print("\n🧪 Running validation tests...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/test_validators.py', 
            '-v', '--tb=short'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running validation tests: {e}")
        return False

def run_simple_api_tests():
    """Run simple API tests that don't require database"""
    print("\n🌐 Running simple API tests...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/test_api.py::TestAPISubmit::test_submit_invalid_data',
            'tests/test_api.py::TestAPISubmit::test_submit_rate_limit',
            '-v', '--tb=short'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running API tests: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 Starting St. Edward Ministry Finder Test Suite")
    print("=" * 50)
    
    # Set up environment
    setup_test_environment()
    
    # Run validation tests first (these should work)
    validation_success = run_validation_tests()
    
    # Run simple API tests
    api_success = run_simple_api_tests()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if validation_success:
        print("✅ Validation tests: PASSED")
    else:
        print("❌ Validation tests: FAILED")
    
    if api_success:
        print("✅ Simple API tests: PASSED")
    else:
        print("❌ Simple API tests: FAILED")
    
    if validation_success and api_success:
        print("\n🎉 All basic tests passed! Your validation system is working.")
        print("\nNext steps:")
        print("1. Set up a test database for full integration tests")
        print("2. Add more comprehensive error handling")
        print("3. Implement the remaining improvements")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return validation_success and api_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 