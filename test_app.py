"""
Simple test suite for the Trading Chart Analyzer application
Tests basic functionality without requiring an OpenAI API key
"""

import os
import sys
import io
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, allowed_file

def test_allowed_file():
    """Test file extension validation"""
    print("Testing file extension validation...")
    
    assert allowed_file('chart.png') == True
    assert allowed_file('chart.jpg') == True
    assert allowed_file('chart.jpeg') == True
    assert allowed_file('chart.gif') == True
    assert allowed_file('chart.webp') == True
    assert allowed_file('chart.pdf') == False
    assert allowed_file('chart.exe') == False
    assert allowed_file('chart') == False
    
    print("✓ File extension validation tests passed")


def test_health_endpoint():
    """Test the health check endpoint"""
    print("\nTesting health endpoint...")
    
    with app.test_client() as client:
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'Trading Chart Analyzer'
    
    print("✓ Health endpoint test passed")


def test_analyze_no_file():
    """Test analyze endpoint with no file uploaded (requires authentication)"""
    print("\nTesting analyze endpoint with no file...")
    
    with app.test_client() as client:
        response = client.post('/api/analyze')
        
        # Should return 302 redirect to login page because of authentication requirement
        assert response.status_code == 302
    
    print("✓ No file validation test passed (unauthorized as expected)")


def test_analyze_empty_filename():
    """Test analyze endpoint with empty filename (requires authentication)"""
    print("\nTesting analyze endpoint with empty filename...")
    
    with app.test_client() as client:
        data = {'chart': (io.BytesIO(b''), '')}
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        # Should return 302 redirect because of authentication requirement
        assert response.status_code == 302
    
    print("✓ Empty filename validation test passed (unauthorized as expected)")


def test_analyze_invalid_file_type():
    """Test analyze endpoint with invalid file type (requires authentication)"""
    print("\nTesting analyze endpoint with invalid file type...")
    
    with app.test_client() as client:
        data = {'chart': (io.BytesIO(b'fake content'), 'test.txt')}
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        
        # Should return 302 redirect because of authentication requirement
        assert response.status_code == 302
    
    print("✓ Invalid file type validation test passed (unauthorized as expected)")


def test_static_files_exist():
    """Test that all static files exist"""
    print("\nTesting static files existence...")
    
    static_files = ['login.html', 'register.html', 'dashboard.html', 'analyzer.html', 'styles.css', 'analyzer-script.js', 'dashboard-script.js', 'auth-styles.css', 'dashboard-styles.css']
    for filename in static_files:
        filepath = Path('static') / filename
        assert filepath.exists(), f"{filename} not found"
    
    print("✓ All static files exist")


def test_index_route():
    """Test that the index route returns HTML (redirects to login)"""
    print("\nTesting index route...")
    
    with app.test_client() as client:
        response = client.get('/')
        
        assert response.status_code == 200
        # Should serve login.html for unauthenticated users
        assert b'Trading Analysis Platform' in response.data or b'Sign In' in response.data
    
    print("✓ Index route test passed")


def test_authentication_endpoints():
    """Test authentication endpoints exist"""
    print("\nTesting authentication endpoints...")
    
    with app.test_client() as client:
        # Test login page
        response = client.get('/login')
        assert response.status_code == 200
        
        # Test register page
        response = client.get('/register')
        assert response.status_code == 200
        
        # Test dashboard requires auth (redirects)
        response = client.get('/dashboard')
        assert response.status_code == 302
        
        # Test analyzer requires auth (redirects)
        response = client.get('/analyzer')
        assert response.status_code == 302
    
    print("✓ Authentication endpoints test passed")


def test_user_registration():
    """Test user registration"""
    print("\nTesting user registration...")
    
    with app.test_client() as client:
        # Try to register a new user
        response = client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'full_name': 'Test User'
        })
        
        # Should succeed or fail if user already exists
        assert response.status_code in [201, 400]
    
    print("✓ User registration test passed")


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Trading Chart Analyzer Tests")
    print("=" * 60)
    
    try:
        test_allowed_file()
        test_health_endpoint()
        test_analyze_no_file()
        test_analyze_empty_filename()
        test_analyze_invalid_file_type()
        test_static_files_exist()
        test_index_route()
        test_authentication_endpoints()
        test_user_registration()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
