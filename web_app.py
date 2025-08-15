#!/usr/bin/env python3
"""
Serverless Flask API for Kelly's User Management System
DynamoDB-powered serverless architecture
"""

import os
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.auth.transport import requests
from google.oauth2 import id_token
from src.models.dynamodb_user import db_user

def create_app():
    """Application factory pattern for serverless deployment."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CORS configuration
    cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, origins=cors_origins)
    
    # Register routes
    register_routes(app)
    
    return app

def register_routes(app):
    """Register all application routes."""
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for load balancers."""
        return jsonify({
            'status': 'healthy',
            'message': 'Serverless API is running with OAuth',
            'version': '2.1.0',
            'architecture': 'AWS Lambda + DynamoDB + OAuth',
            'oauth_enabled': True
        })
    
    @app.route('/api/auth/google', methods=['POST'])
    def google_oauth():
        """Handle Google OAuth authentication."""
        try:
            # Get the ID token from the request
            data = request.get_json()
            if not data or not data.get('credential'):
                return jsonify({'error': 'Missing Google credential'}), 400
            
            token = data['credential']
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            
            if not client_id:
                return jsonify({'error': 'Google OAuth not configured'}), 500
            
            # Verify the token with Google
            try:
                idinfo = id_token.verify_oauth2_token(
                    token, requests.Request(), client_id
                )
                
                # Extract user information
                google_id = idinfo['sub']
                email = idinfo['email']
                name = idinfo.get('name', '')
                given_name = idinfo.get('given_name', '')
                family_name = idinfo.get('family_name', '')
                picture = idinfo.get('picture', '')
                
                # Check if user exists by Google ID or email
                user = None
                try:
                    user = db_user.get_user_by_oauth_id('google', google_id)
                except:
                    # User doesn't exist with this Google ID, try email
                    try:
                        user = db_user.get_user_by_email(email)
                        if user:
                            # Link this Google account to existing user
                            db_user.link_oauth_account(user['id'], 'google', google_id)
                    except:
                        pass
                
                # Create new user if doesn't exist
                if not user:
                    user_data = {
                        'email': email,
                        'first_name': given_name or name.split(' ')[0] if name else '',
                        'last_name': family_name or (name.split(' ')[1] if ' ' in name else ''),
                        'username': email.split('@')[0],  # Use email prefix as username
                        'oauth_provider': 'google',
                        'oauth_id': google_id,
                        'profile_picture': picture
                    }
                    
                    # Ensure unique username
                    base_username = user_data['username']
                    counter = 1
                    while True:
                        try:
                            existing = db_user.get_user_by_username(user_data['username'])
                            if not existing:
                                break
                            user_data['username'] = f"{base_username}_{counter}"
                            counter += 1
                        except:
                            break
                    
                    user = db_user.create_oauth_user(**user_data)
                
                # Generate JWT token for session management
                jwt_payload = {
                    'user_id': user['id'],
                    'email': user['email'],
                    'oauth_provider': 'google'
                }
                jwt_token = jwt.encode(
                    jwt_payload,
                    app.config['SECRET_KEY'],
                    algorithm='HS256'
                )
                
                return jsonify({
                    'message': 'OAuth login successful',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'is_active': user.get('is_active', True),
                        'profile_picture': user.get('profile_picture', ''),
                        'oauth_provider': 'google'
                    },
                    'token': jwt_token
                }), 200
                
            except ValueError as e:
                return jsonify({'error': f'Invalid Google token: {str(e)}'}), 401
                
        except Exception as e:
            return jsonify({
                'error': 'OAuth authentication failed',
                'details': str(e)
            }), 500
    
    @app.route('/api/users', methods=['GET'])
    def get_users():
        """Get all users from DynamoDB."""
        try:
            users = db_user.get_all_users()
            return jsonify(users)
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch users',
                'details': str(e)
            }), 500
    
    @app.route('/api/users', methods=['POST'])
    def create_user():
        """Create a new user in DynamoDB."""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['username', 'email', 'first_name', 'last_name']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'error': 'Missing required fields',
                    'required': required_fields
                }), 400
            
            # Create new user
            new_user = db_user.create_user(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            
            return jsonify(new_user), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({
                'error': 'Failed to create user',
                'details': str(e)
            }), 500
    
    @app.route('/api/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        """Get a specific user by ID from DynamoDB."""
        try:
            user = db_user.get_user_by_id(user_id)
            if user is None:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(user)
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch user',
                'details': str(e)
            }), 500
    
    @app.route('/api/users/<user_id>', methods=['PUT'])
    def update_user(user_id):
        """Update a specific user in DynamoDB."""
        try:
            data = request.get_json()
            
            # Update user
            updated_user = db_user.update_user(user_id, **data)
            return jsonify(updated_user)
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({
                'error': 'Failed to update user',
                'details': str(e)
            }), 500
    
    @app.route('/api/users/<user_id>', methods=['DELETE'])
    def delete_user(user_id):
        """Delete a specific user from DynamoDB."""
        try:
            db_user.delete_user(user_id)
            return jsonify({'message': 'User deleted successfully'}), 200
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({
                'error': 'Failed to delete user',
                'details': str(e)
            }), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Authenticate user login."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data or not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username and password are required'}), 400
            
            username = data['username']
            password = data['password']
            
            # Get user by username
            user = db_user.get_user_by_username(username)
            if not user:
                # Try by email if username doesn't work
                user = db_user.get_user_by_email(username)
            
            if not user:
                return jsonify({'error': 'Invalid username or password'}), 401
            
            # For demo purposes, we'll use a simple password check
            # In production, you'd hash passwords and compare hashes
            # For now, we'll check if password equals the first_name (simple demo)
            if password != user.get('first_name', ''):
                return jsonify({'error': 'Invalid username or password'}), 401
            
            # Return user info (excluding sensitive data)
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'is_active': user['is_active']
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'error': 'Login failed',
                'details': str(e)
            }), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        """Handle user logout."""
        return jsonify({'message': 'Logout successful'}), 200

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # For local testing
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("Starting Serverless Flask API (local mode)...")
    print(f"API available at: http://{host}:{port}/api")
    print("Health check: /api/health")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(debug=True, host=host, port=port)