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
from src.models.dynamodb_todo import db_todo

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
    
    # Todo Management Routes
    @app.route('/api/todos', methods=['GET'])
    def get_todos():
        """Get all todos for the authenticated user."""
        try:
            # In a real app, you'd get user_id from JWT token
            # For demo, we'll use query parameter or default to Kelly's user ID
            user_id = request.args.get('user_id', '2365999676')  # Kelly's user ID
            
            todos = db_todo.get_user_todos(user_id)
            return jsonify(todos)
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch todos',
                'details': str(e)
            }), 500
    
    @app.route('/api/todos', methods=['POST'])
    def create_todo():
        """Create a new todo for the authenticated user."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data or not data.get('title'):
                return jsonify({'error': 'Title is required'}), 400
            
            # In a real app, you'd get user_id from JWT token
            user_id = data.get('user_id', '2365999676')  # Default to Kelly's user ID
            
            new_todo = db_todo.create_todo(
                user_id=user_id,
                title=data['title'],
                description=data.get('description', ''),
                priority=data.get('priority', 'medium'),
                due_date=data.get('due_date')
            )
            
            return jsonify(new_todo), 201
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to create todo',
                'details': str(e)
            }), 500
    
    @app.route('/api/todos/<todo_id>', methods=['GET'])
    def get_todo(todo_id):
        """Get a specific todo by ID."""
        try:
            todo = db_todo.get_todo_by_id(todo_id)
            if not todo:
                return jsonify({'error': 'Todo not found'}), 404
            return jsonify(todo)
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch todo',
                'details': str(e)
            }), 500
    
    @app.route('/api/todos/<todo_id>', methods=['PUT'])
    def update_todo(todo_id):
        """Update a specific todo."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Remove fields that shouldn't be updated directly
            update_data = {k: v for k, v in data.items() 
                          if k in ['title', 'description', 'completed', 'priority', 'due_date']}
            
            updated_todo = db_todo.update_todo(todo_id, **update_data)
            return jsonify(updated_todo)
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to update todo',
                'details': str(e)
            }), 500
    
    @app.route('/api/todos/<todo_id>', methods=['DELETE'])
    def delete_todo(todo_id):
        """Delete a specific todo."""
        try:
            success = db_todo.delete_todo(todo_id)
            if success:
                return jsonify({'message': 'Todo deleted successfully'}), 200
            else:
                return jsonify({'error': 'Failed to delete todo'}), 500
                
        except Exception as e:
            return jsonify({
                'error': 'Failed to delete todo',
                'details': str(e)
            }), 500
    
    @app.route('/api/todos/<todo_id>/complete', methods=['PUT'])
    def toggle_todo_completion(todo_id):
        """Toggle completion status of a todo."""
        try:
            data = request.get_json()
            completed = data.get('completed', True) if data else True
            
            updated_todo = db_todo.mark_completed(todo_id, completed)
            return jsonify(updated_todo)
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to update todo completion',
                'details': str(e)
            }), 500

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
    
    # Check if running in production/background mode
    debug_mode = os.environ.get('FLASK_DEBUG', '').lower() in ('true', '1', 'yes')
    
    # Run the Flask app (disable debug/reloader for stable background operation)
    app.run(debug=debug_mode, host=host, port=port, use_reloader=debug_mode)