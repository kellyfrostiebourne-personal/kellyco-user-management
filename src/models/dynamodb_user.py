"""
DynamoDB User model for serverless architecture
Replaces SQLAlchemy model for better Lambda performance
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

class DynamoDBUser:
    """User model using DynamoDB for serverless architecture."""
    
    def __init__(self):
        """Initialize DynamoDB connection."""
        # Configure for local development vs production
        if os.environ.get('DYNAMODB_LOCAL'):
            # Local DynamoDB
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:8000',
                region_name='us-east-1',
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy'
            )
        else:
            # Production DynamoDB (AWS Lambda or local with AWS credentials)
            region_name = os.environ.get('AWS_REGION', 'us-east-1')
            self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        
        self.table_name = os.environ.get('DYNAMODB_TABLE', 'kelly-user-management-dev-users')
        self.table = self.dynamodb.Table(self.table_name)
    
    def to_dict(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB item to standard dictionary format."""
        if not item:
            return {}
        
        return {
            'id': int(item.get('id', 0)),
            'username': item.get('username', ''),
            'email': item.get('email', ''),
            'first_name': item.get('first_name', ''),
            'last_name': item.get('last_name', ''),
            'created_at': item.get('created_at', ''),
            'updated_at': item.get('updated_at'),
            'is_active': item.get('is_active', True),
            'oauth_provider': item.get('oauth_provider', ''),
            'oauth_id': item.get('oauth_id', ''),
            'profile_picture': item.get('profile_picture', '')
        }
    
    def create_user(self, username: str, email: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """Create a new user in DynamoDB."""
        try:
            # Generate unique ID
            user_id = str(uuid.uuid4().int)[:10]  # Use first 10 digits of UUID as integer string
            current_time = datetime.utcnow().isoformat()
            
            # Check if username already exists
            if self.get_user_by_username(username):
                raise ValueError("Username already exists")
            
            # Check if email already exists
            if self.get_user_by_email(email):
                raise ValueError("Email already exists")
            
            # Create user item
            user_item = {
                'id': user_id,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'created_at': current_time,
                'updated_at': None,
                'is_active': True
            }
            
            # Put item in DynamoDB
            self.table.put_item(Item=user_item)
            
            return self.to_dict(user_item)
            
        except ClientError as e:
            print(f"DynamoDB error creating user: {e}")
            raise Exception(f"Failed to create user: {str(e)}")
        except Exception as e:
            print(f"Error creating user: {e}")
            raise e
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from DynamoDB."""
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            return [self.to_dict(item) for item in items]
            
        except ClientError as e:
            print(f"DynamoDB error getting all users: {e}")
            raise Exception(f"Failed to get users: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from DynamoDB."""
        try:
            response = self.table.get_item(Key={'id': str(user_id)})
            item = response.get('Item')
            
            if item:
                return self.to_dict(item)
            return None
            
        except ClientError as e:
            print(f"DynamoDB error getting user by ID: {e}")
            raise Exception(f"Failed to get user: {str(e)}")
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username using GSI."""
        try:
            response = self.table.query(
                IndexName='username-index',
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            
            items = response.get('Items', [])
            if items:
                return self.to_dict(items[0])
            return None
            
        except ClientError as e:
            print(f"DynamoDB error getting user by username: {e}")
            raise Exception(f"Failed to get user: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email using GSI."""
        try:
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            items = response.get('Items', [])
            if items:
                return self.to_dict(items[0])
            return None
            
        except ClientError as e:
            print(f"DynamoDB error getting user by email: {e}")
            raise Exception(f"Failed to get user: {str(e)}")
    
    def update_user(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Update user in DynamoDB."""
        try:
            # Check if user exists
            existing_user = self.get_user_by_id(user_id)
            if not existing_user:
                raise ValueError("User not found")
            
            # Build update expression
            update_expression = "SET updated_at = :updated_at"
            expression_values = {':updated_at': datetime.utcnow().isoformat()}
            
            for key, value in kwargs.items():
                if key in ['first_name', 'last_name', 'email', 'is_active']:
                    update_expression += f", {key} = :{key}"
                    expression_values[f":{key}"] = value
            
            # Check email uniqueness if updating email
            if 'email' in kwargs and kwargs['email'] != existing_user['email']:
                existing_email_user = self.get_user_by_email(kwargs['email'])
                if existing_email_user and existing_email_user['id'] != int(user_id):
                    raise ValueError("Email already exists")
            
            # Update item
            response = self.table.update_item(
                Key={'id': str(user_id)},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return self.to_dict(response['Attributes'])
            
        except ClientError as e:
            print(f"DynamoDB error updating user: {e}")
            raise Exception(f"Failed to update user: {str(e)}")
        except Exception as e:
            print(f"Error updating user: {e}")
            raise e
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user from DynamoDB."""
        try:
            # Check if user exists
            existing_user = self.get_user_by_id(user_id)
            if not existing_user:
                raise ValueError("User not found")
            
            # Delete item
            self.table.delete_item(Key={'id': str(user_id)})
            return True
            
        except ClientError as e:
            print(f"DynamoDB error deleting user: {e}")
            raise Exception(f"Failed to delete user: {str(e)}")
        except Exception as e:
            print(f"Error deleting user: {e}")
            raise e
    
    def create_oauth_user(self, email: str, first_name: str, last_name: str, 
                         username: str, oauth_provider: str, oauth_id: str, 
                         profile_picture: str = '') -> Dict[str, Any]:
        """Create a new OAuth user in DynamoDB."""
        try:
            # Generate unique ID
            user_id = str(uuid.uuid4().int)[:10]  # Use first 10 digits of UUID as integer string
            current_time = datetime.utcnow().isoformat()
            
            # Create user item with OAuth data
            user_item = {
                'id': user_id,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'created_at': current_time,
                'updated_at': None,
                'is_active': True,
                'oauth_provider': oauth_provider,
                'oauth_id': oauth_id,
                'profile_picture': profile_picture
            }
            
            # Put item in DynamoDB
            self.table.put_item(Item=user_item)
            
            return self.to_dict(user_item)
            
        except ClientError as e:
            print(f"DynamoDB error creating OAuth user: {e}")
            raise Exception(f"Failed to create OAuth user: {str(e)}")
        except Exception as e:
            print(f"Error creating OAuth user: {e}")
            raise e
    
    def get_user_by_oauth_id(self, provider: str, oauth_id: str) -> Optional[Dict[str, Any]]:
        """Get user by OAuth provider and ID."""
        try:
            response = self.table.scan(
                FilterExpression='oauth_provider = :provider AND oauth_id = :oauth_id',
                ExpressionAttributeValues={
                    ':provider': provider,
                    ':oauth_id': oauth_id
                }
            )
            
            items = response.get('Items', [])
            if items:
                return self.to_dict(items[0])
            return None
            
        except ClientError as e:
            print(f"DynamoDB error getting user by OAuth ID: {e}")
            raise Exception(f"Failed to get user: {str(e)}")
    
    def link_oauth_account(self, user_id: str, provider: str, oauth_id: str) -> Dict[str, Any]:
        """Link OAuth account to existing user."""
        try:
            update_expression = "SET oauth_provider = :provider, oauth_id = :oauth_id, updated_at = :updated_at"
            expression_values = {
                ':provider': provider,
                ':oauth_id': oauth_id,
                ':updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.table.update_item(
                Key={'id': str(user_id)},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return self.to_dict(response['Attributes'])
            
        except ClientError as e:
            print(f"DynamoDB error linking OAuth account: {e}")
            raise Exception(f"Failed to link OAuth account: {str(e)}")

# Global instance for use in Flask routes
db_user = DynamoDBUser()
