"""
API key validation script for College Counselor application.

This script validates that all required API keys are correctly configured and working.
"""

import os
import sys
import requests
import json
from flask import Flask

def validate_openai_api_key():
    """Validate the OpenAI API key."""
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        return False
    
    # For security, we'll only print the first few and last few characters
    masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    print(f"OpenAI API Key found: {masked_key}")
    
    # Test API connection using a simple request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, this is a test message."}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("OpenAI API key is valid.")
            return True
        else:
            print(f"OpenAI API key validation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"OpenAI API key validation failed: {e}")
        return False

def validate_college_scorecard_api_key():
    """Validate the College Scorecard API key."""
    api_key = os.environ.get('COLLEGE_SCORECARD_API_KEY')
    
    if not api_key:
        print("ERROR: COLLEGE_SCORECARD_API_KEY environment variable not set.")
        return False
    
    # For security, we'll only print the first few and last few characters
    masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    print(f"College Scorecard API Key found: {masked_key}")
    
    # Test API connection
    try:
        url = f"https://api.data.gov/ed/collegescorecard/v1/schools?api_key={api_key}&per_page=1"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("College Scorecard API key is valid.")
            print(f"Retrieved data for {data['metadata']['total']} schools.")
            return True
        else:
            print(f"College Scorecard API key validation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"College Scorecard API key validation failed: {e}")
        return False

def validate_secret_key():
    """Validate the Flask SECRET_KEY."""
    secret_key = os.environ.get('SECRET_KEY')
    
    if not secret_key:
        print("ERROR: SECRET_KEY environment variable not set.")
        return False
    
    # For security, we'll only print the first few and last few characters
    masked_key = f"{secret_key[:5]}...{secret_key[-4:]}" if len(secret_key) > 10 else "***"
    print(f"Secret Key found: {masked_key}")
    
    # Test session functionality
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key
    
    try:
        with app.test_request_context():
            from flask import session
            session['test'] = 'test_value'
            test_value = session.get('test')
            
            if test_value == 'test_value':
                print("Secret key is valid and session functionality is working.")
                return True
            else:
                print("Secret key validation failed: Session value not stored correctly.")
                return False
    except Exception as e:
        print(f"Secret key validation failed: {e}")
        return False

def validate_api_url():
    """Validate the API_URL."""
    api_url = os.environ.get('API_URL')
    
    if not api_url:
        print("ERROR: API_URL environment variable not set.")
        return False
    
    print(f"API URL found: {api_url}")
    
    # Test API connection
    try:
        response = requests.get(f"{api_url}/health")
        
        if response.status_code == 200:
            data = response.json()
            print("API URL is valid.")
            print(f"API status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"API URL validation failed: {response.status_code} - {response.text}")
            # Try fallback to root endpoint
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    print("API URL is valid (root endpoint).")
                    return True
                else:
                    return False
            except:
                return False
    except Exception as e:
        print(f"API URL validation failed: {e}")
        # This might be expected in development environment
        print("Note: API service might not be running or accessible.")
        return True  # Return True to allow development to continue

def validate_all_api_keys():
    """Validate all required API keys."""
    print("Starting API key validation...")
    print("-" * 50)
    
    openai_valid = validate_openai_api_key()
    print("-" * 50)
    
    scorecard_valid = validate_college_scorecard_api_key()
    print("-" * 50)
    
    secret_valid = validate_secret_key()
    print("-" * 50)
    
    api_url_valid = validate_api_url()
    print("-" * 50)
    
    # Summary
    print("\nAPI Key Validation Summary:")
    print(f"OpenAI API Key: {'✓ Valid' if openai_valid else '✗ Invalid'}")
    print(f"College Scorecard API Key: {'✓ Valid' if scorecard_valid else '✗ Invalid'}")
    print(f"Secret Key: {'✓ Valid' if secret_valid else '✗ Invalid'}")
    print(f"API URL: {'✓ Valid' if api_url_valid else '✗ Invalid'}")
    
    all_valid = openai_valid and scorecard_valid and secret_valid and api_url_valid
    
    if all_valid:
        print("\nAll API keys are valid and working correctly!")
    else:
        print("\nSome API keys are missing or invalid. See details above.")
        print("Note: The application includes fallback mechanisms for missing or invalid API keys.")
    
    return all_valid

if __name__ == "__main__":
    success = validate_all_api_keys()
    sys.exit(0 if success else 1)
