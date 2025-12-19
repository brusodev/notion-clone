#!/usr/bin/env python3
"""
Test script for Notion Clone API registration flow
Tests the complete registration process: user creation, workspace creation, and token generation
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1"
TIMEOUT = 10

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")

def test_health_check():
    """Test if API is running"""
    print_header("1. Testing API Health Check")
    
    try:
        # Health check is at root level, not under /api/v1
        health_url = "http://localhost:8000/health"
        response = requests.get(health_url, timeout=TIMEOUT)
        if response.status_code == 200:
            print_success(f"API is running: {response.json()}")
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API at http://localhost:8000")
        print_info("Make sure the backend is running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_registration(email, name, password):
    """Test user registration"""
    print_header(f"2. Testing User Registration")
    print_info(f"Email: {email}")
    print_info(f"Name: {name}")
    print_info(f"Password length: {len(password)} characters")
    
    payload = {
        "email": email,
        "name": name,
        "password": password,
        "password_confirm": password
    }
    
    try:
        print_info(f"Sending request to {API_URL}/auth/register...")
        response = requests.post(
            f"{API_URL}/auth/register",
            json=payload,
            timeout=TIMEOUT
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Registration successful!")
            print(f"  - Access Token: {data['access_token'][:50]}...")
            print(f"  - Refresh Token: {data['refresh_token'][:50]}...")
            print(f"  - Token Type: {data['token_type']}")
            print(f"  - User ID: {data['user']['id']}")
            print(f"  - User Email: {data['user']['email']}")
            print(f"  - User Name: {data['user']['name']}")
            return data
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print_error(f"Registration failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            print(f"\nFull response: {json.dumps(response.json(), indent=2)}")
            return None
            
    except requests.exceptions.Timeout:
        print_error(f"Request timed out after {TIMEOUT} seconds")
        return None
    except Exception as e:
        print_error(f"Registration request failed: {str(e)}")
        return None

def test_login(email, password):
    """Test user login"""
    print_header("3. Testing User Login")
    print_info(f"Email: {email}")
    
    payload = {
        "username": email,  # FastAPI OAuth2PasswordRequestForm uses 'username'
        "password": password
    }
    
    try:
        print_info(f"Sending request to {API_URL}/auth/login...")
        response = requests.post(
            f"{API_URL}/auth/login",
            data=payload,  # Use data instead of json for form submission
            timeout=TIMEOUT
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login successful!")
            print(f"  - Access Token: {data['access_token'][:50]}...")
            print(f"  - Token Type: {data['token_type']}")
            return data
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print_error(f"Login failed with status {response.status_code}")
            print_error(f"Error: {error_detail}")
            return None
            
    except Exception as e:
        print_error(f"Login request failed: {str(e)}")
        return None

def test_get_current_user(access_token):
    """Test getting current user info"""
    print_header("4. Testing Get Current User")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        print_info(f"Sending request to {API_URL}/auth/me...")
        response = requests.get(
            f"{API_URL}/auth/me",
            headers=headers,
            timeout=TIMEOUT
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Current user retrieved successfully!")
            print(f"  - User ID: {data['id']}")
            print(f"  - Email: {data['email']}")
            print(f"  - Name: {data['name']}")
            print(f"  - Active: {data['is_active']}")
            return data
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print_error(f"Failed to get current user: {response.status_code}")
            print_error(f"Error: {error_detail}")
            return None
            
    except Exception as e:
        print_error(f"Get current user request failed: {str(e)}")
        return None

def run_full_test():
    """Run the complete test suite"""
    print_header("NOTION CLONE API - REGISTRATION TEST SUITE")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"API URL: {API_URL}")
    
    # Test 1: Health check
    if not test_health_check():
        print_error("\nAPI is not accessible. Exiting tests.")
        return False
    
    # Generate unique email for testing (use a valid domain)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    test_email = f"test.{timestamp}@example.com"
    test_name = f"Test User {timestamp}"
    test_password = f"TestPassword{timestamp}!"  # Must be at least 8 characters
    
    # Test 2: Registration
    registration_data = test_registration(test_email, test_name, test_password)
    if not registration_data:
        print_error("\nRegistration failed. Exiting tests.")
        return False
    
    # Test 3: Login
    login_data = test_login(test_email, test_password)
    if not login_data:
        print_error("\nLogin failed. Exiting tests.")
        return False
    
    # Test 4: Get current user
    user_data = test_get_current_user(registration_data['access_token'])
    if not user_data:
        print_error("\nGet current user failed. Exiting tests.")
        return False
    
    # Final summary
    print_header("TEST SUMMARY")
    print_success("All tests passed! ✓")
    print(f"\nTest Account Created:")
    print(f"  - Email: {test_email}")
    print(f"  - Name: {test_name}")
    print(f"  - Password: {test_password}")
    print(f"\nYou can now test the frontend with this account!")
    
    return True

if __name__ == "__main__":
    try:
        success = run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)
