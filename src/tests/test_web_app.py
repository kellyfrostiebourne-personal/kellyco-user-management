"""
Tests for the Flask web application.
"""

import pytest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from simple_web_app import create_app


@pytest.fixture
def app():
    """Create a test Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestWebApp:
    """Test class for Flask web application."""

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['message'] == 'Simple API is running'
        assert data['version'] == '1.0.0'

    def test_get_users(self, client):
        """Test getting all users."""
        response = client.get('/api/users')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2  # Should have at least 2 pre-loaded users
        
        # Check user structure
        user = data[0]
        assert 'id' in user
        assert 'username' in user
        assert 'email' in user
        assert 'first_name' in user
        assert 'last_name' in user
        assert 'is_active' in user

    def test_create_user_success(self, client):
        """Test creating a new user successfully."""
        new_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(new_user),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['first_name'] == 'Test'
        assert data['last_name'] == 'User'
        assert data['is_active'] is True

    def test_create_user_missing_fields(self, client):
        """Test creating a user with missing fields."""
        incomplete_user = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing first_name and last_name
        }
        
        response = client.post('/api/users',
                             data=json.dumps(incomplete_user),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required fields' in data['error']

    def test_create_duplicate_user(self, client):
        """Test creating a user with duplicate username."""
        duplicate_user = {
            'username': 'Kelly',  # This username already exists
            'email': 'duplicate@example.com',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }
        
        response = client.post('/api/users',
                             data=json.dumps(duplicate_user),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Username already exists' in data['error']

    def test_login_success(self, client):
        """Test successful login."""
        login_data = {
            'username': 'Kelly',
            'password': 'Kelly'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['username'] == 'Kelly'
        assert data['user']['first_name'] == 'Kelly'

    def test_login_with_email(self, client):
        """Test login using email instead of username."""
        login_data = {
            'username': 'kelly@kellyco.com',  # Using email
            'password': 'Kelly'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            'username': 'Kelly',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid username or password' in data['error']

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            'username': 'nonexistent',
            'password': 'password'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid username or password' in data['error']

    def test_login_missing_fields(self, client):
        """Test login with missing username or password."""
        # Missing password
        login_data = {'username': 'Kelly'}
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Username and password are required' in data['error']

    def test_logout(self, client):
        """Test logout endpoint."""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['message'] == 'Logout successful'
