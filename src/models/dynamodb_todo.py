"""
DynamoDB Todo model for todo list functionality
User-specific todo management
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

class DynamoDBTodo:
    """Todo model using DynamoDB for serverless architecture."""
    
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
        
        self.table_name = os.environ.get('DYNAMODB_TODO_TABLE', 'kelly-user-management-dev-todos')
        self.table = self.dynamodb.Table(self.table_name)
    
    def to_dict(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB item to standard dictionary format."""
        return {
            'id': item.get('id'),
            'user_id': item.get('user_id'),
            'title': item.get('title'),
            'description': item.get('description', ''),
            'completed': item.get('completed', False),
            'priority': item.get('priority', 'medium'),
            'due_date': item.get('due_date'),
            'created_at': item.get('created_at'),
            'updated_at': item.get('updated_at')
        }
    
    def create_todo(self, user_id: str, title: str, description: str = '', 
                   priority: str = 'medium', due_date: str = None) -> Dict[str, Any]:
        """Create a new todo item."""
        try:
            todo_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            todo_item = {
                'id': todo_id,
                'user_id': str(user_id),
                'title': title,
                'description': description,
                'completed': False,
                'priority': priority,
                'due_date': due_date,
                'created_at': now,
                'updated_at': None
            }
            
            self.table.put_item(Item=todo_item)
            return self.to_dict(todo_item)
            
        except ClientError as e:
            print(f"DynamoDB error creating todo: {e}")
            raise Exception(f"Failed to create todo: {str(e)}")
    
    def get_user_todos(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all todos for a specific user."""
        try:
            response = self.table.query(
                IndexName='user-id-index',
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': str(user_id)}
            )
            
            items = response.get('Items', [])
            return [self.to_dict(item) for item in items]
            
        except ClientError as e:
            print(f"DynamoDB error getting user todos: {e}")
            raise Exception(f"Failed to get todos: {str(e)}")
    
    def get_todo_by_id(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific todo by ID."""
        try:
            response = self.table.get_item(Key={'id': str(todo_id)})
            item = response.get('Item')
            
            if item:
                return self.to_dict(item)
            return None
            
        except ClientError as e:
            print(f"DynamoDB error getting todo by ID: {e}")
            raise Exception(f"Failed to get todo: {str(e)}")
    
    def update_todo(self, todo_id: str, **kwargs) -> Dict[str, Any]:
        """Update a todo item."""
        try:
            update_expression = "SET updated_at = :updated_at"
            expression_values = {':updated_at': datetime.utcnow().isoformat()}
            
            # Build update expression for provided fields
            allowed_fields = ['title', 'description', 'completed', 'priority', 'due_date']
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_expression += f", {field} = :{field}"
                    expression_values[f':{field}'] = value
            
            response = self.table.update_item(
                Key={'id': str(todo_id)},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return self.to_dict(response['Attributes'])
            
        except ClientError as e:
            print(f"DynamoDB error updating todo: {e}")
            raise Exception(f"Failed to update todo: {str(e)}")
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo item."""
        try:
            self.table.delete_item(Key={'id': str(todo_id)})
            return True
            
        except ClientError as e:
            print(f"DynamoDB error deleting todo: {e}")
            raise Exception(f"Failed to delete todo: {str(e)}")
    
    def mark_completed(self, todo_id: str, completed: bool = True) -> Dict[str, Any]:
        """Mark a todo as completed or incomplete."""
        return self.update_todo(todo_id, completed=completed)

# Global instance for use in Flask routes
db_todo = DynamoDBTodo()
