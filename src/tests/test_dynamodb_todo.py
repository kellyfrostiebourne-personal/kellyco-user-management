"""
Tests for the DynamoDB Todo model.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock
from moto import mock_dynamodb
import boto3

from src.models.dynamodb_todo import DynamoDBTodo


class TestDynamoDBTodo:
    """Test cases for DynamoDB Todo model."""

    @mock_dynamodb
    def setup_method(self, method):
        """Set up test environment with mocked DynamoDB."""
        # Mock environment for local DynamoDB
        with patch.dict('os.environ', {'DYNAMODB_LOCAL': 'true'}):
            self.todo_model = DynamoDBTodo()
            
        # Create the table
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url='http://localhost:8000',
            region_name='us-east-1',
            aws_access_key_id='dummy',
            aws_secret_access_key='dummy'
        )
        
        dynamodb.create_table(
            TableName='kelly-user-management-dev-todos',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user-id-index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    def test_to_dict_with_valid_item(self):
        """Test converting DynamoDB item to dictionary format."""
        todo_model = DynamoDBTodo()
        
        dynamo_item = {
            'id': 'todo-123',
            'user_id': 'user-456',
            'title': 'Test Todo',
            'description': 'Test description',
            'completed': False,
            'priority': 'high',
            'due_date': '2023-12-31',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': None
        }
        
        result = todo_model.to_dict(dynamo_item)
        
        expected = {
            'id': 'todo-123',
            'user_id': 'user-456',
            'title': 'Test Todo',
            'description': 'Test description',
            'completed': False,
            'priority': 'high',
            'due_date': '2023-12-31',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': None
        }
        
        assert result == expected

    def test_to_dict_with_missing_fields(self):
        """Test converting DynamoDB item with missing fields."""
        todo_model = DynamoDBTodo()
        
        incomplete_item = {
            'id': 'todo-123',
            'user_id': 'user-456',
            'title': 'Test Todo'
            # Missing other fields
        }
        
        result = todo_model.to_dict(incomplete_item)
        
        expected = {
            'id': 'todo-123',
            'user_id': 'user-456',
            'title': 'Test Todo',
            'description': '',
            'completed': False,
            'priority': 'medium',
            'due_date': None,
            'created_at': None,
            'updated_at': None
        }
        
        assert result == expected

    @mock_dynamodb
    @patch('src.models.dynamodb_todo.uuid.uuid4')
    @patch('src.models.dynamodb_todo.datetime')
    def test_create_todo_success(self, mock_datetime, mock_uuid):
        """Test successful todo creation."""
        # Setup mocks
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = MagicMock(return_value='test-todo-id')
        mock_datetime.utcnow.return_value.isoformat.return_value = '2023-01-01T00:00:00'
        
        todo_model = DynamoDBTodo()
        
        # Mock the table.put_item method
        todo_model.table = MagicMock()
        todo_model.table.put_item = MagicMock()
        
        result = todo_model.create_todo(
            user_id='user-123',
            title='Test Todo',
            description='Test description',
            priority='high',
            due_date='2023-12-31'
        )
        
        # Verify the result
        expected = {
            'id': 'test-todo-id',
            'user_id': 'user-123',
            'title': 'Test Todo',
            'description': 'Test description',
            'completed': False,
            'priority': 'high',
            'due_date': '2023-12-31',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': None
        }
        
        assert result == expected
        
        # Verify put_item was called with correct data
        todo_model.table.put_item.assert_called_once()
        call_args = todo_model.table.put_item.call_args[1]['Item']
        assert call_args['id'] == 'test-todo-id'
        assert call_args['user_id'] == 'user-123'
        assert call_args['title'] == 'Test Todo'

    @mock_dynamodb
    def test_get_user_todos_success(self):
        """Test successful retrieval of user todos."""
        todo_model = DynamoDBTodo()
        
        # Mock the table.query method
        mock_response = {
            'Items': [
                {
                    'id': 'todo-1',
                    'user_id': 'user-123',
                    'title': 'Todo 1',
                    'description': 'Description 1',
                    'completed': False,
                    'priority': 'high',
                    'due_date': None,
                    'created_at': '2023-01-01T00:00:00',
                    'updated_at': None
                },
                {
                    'id': 'todo-2',
                    'user_id': 'user-123',
                    'title': 'Todo 2',
                    'description': 'Description 2',
                    'completed': True,
                    'priority': 'low',
                    'due_date': '2023-12-31',
                    'created_at': '2023-01-01T00:00:00',
                    'updated_at': '2023-01-02T00:00:00'
                }
            ]
        }
        
        todo_model.table = MagicMock()
        todo_model.table.query.return_value = mock_response
        
        result = todo_model.get_user_todos('user-123')
        
        assert len(result) == 2
        assert result[0]['id'] == 'todo-1'
        assert result[1]['id'] == 'todo-2'
        
        # Verify query was called with correct parameters
        todo_model.table.query.assert_called_once_with(
            IndexName='user-id-index',
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': 'user-123'}
        )

    @mock_dynamodb
    def test_get_todo_by_id_success(self):
        """Test successful retrieval of todo by ID."""
        todo_model = DynamoDBTodo()
        
        mock_response = {
            'Item': {
                'id': 'todo-123',
                'user_id': 'user-456',
                'title': 'Test Todo',
                'description': 'Test description',
                'completed': False,
                'priority': 'medium',
                'due_date': None,
                'created_at': '2023-01-01T00:00:00',
                'updated_at': None
            }
        }
        
        todo_model.table = MagicMock()
        todo_model.table.get_item.return_value = mock_response
        
        result = todo_model.get_todo_by_id('todo-123')
        
        assert result['id'] == 'todo-123'
        assert result['title'] == 'Test Todo'
        
        # Verify get_item was called with correct key
        todo_model.table.get_item.assert_called_once_with(
            Key={'id': 'todo-123'}
        )

    @mock_dynamodb
    def test_get_todo_by_id_not_found(self):
        """Test todo retrieval when todo doesn't exist."""
        todo_model = DynamoDBTodo()
        
        mock_response = {}  # No Item key means not found
        
        todo_model.table = MagicMock()
        todo_model.table.get_item.return_value = mock_response
        
        result = todo_model.get_todo_by_id('nonexistent-todo')
        
        assert result is None

    @mock_dynamodb
    @patch('src.models.dynamodb_todo.datetime')
    def test_update_todo_success(self, mock_datetime):
        """Test successful todo update."""
        mock_datetime.utcnow.return_value.isoformat.return_value = '2023-01-02T00:00:00'
        
        todo_model = DynamoDBTodo()
        
        mock_response = {
            'Attributes': {
                'id': 'todo-123',
                'user_id': 'user-456',
                'title': 'Updated Todo',
                'description': 'Updated description',
                'completed': True,
                'priority': 'low',
                'due_date': '2023-12-31',
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-02T00:00:00'
            }
        }
        
        todo_model.table = MagicMock()
        todo_model.table.update_item.return_value = mock_response
        
        result = todo_model.update_todo(
            'todo-123',
            title='Updated Todo',
            description='Updated description',
            completed=True,
            priority='low',
            due_date='2023-12-31'
        )
        
        assert result['id'] == 'todo-123'
        assert result['title'] == 'Updated Todo'
        assert result['completed'] is True
        
        # Verify update_item was called
        todo_model.table.update_item.assert_called_once()

    @mock_dynamodb
    def test_delete_todo_success(self):
        """Test successful todo deletion."""
        todo_model = DynamoDBTodo()
        
        todo_model.table = MagicMock()
        todo_model.table.delete_item.return_value = {}
        
        result = todo_model.delete_todo('todo-123')
        
        assert result is True
        
        # Verify delete_item was called with correct key
        todo_model.table.delete_item.assert_called_once_with(
            Key={'id': 'todo-123'}
        )

    @mock_dynamodb
    @patch('src.models.dynamodb_todo.datetime')
    def test_mark_completed_success(self, mock_datetime):
        """Test successful todo completion toggle."""
        mock_datetime.utcnow.return_value.isoformat.return_value = '2023-01-02T00:00:00'
        
        todo_model = DynamoDBTodo()
        
        mock_response = {
            'Attributes': {
                'id': 'todo-123',
                'user_id': 'user-456',
                'title': 'Test Todo',
                'description': 'Test description',
                'completed': True,
                'priority': 'medium',
                'due_date': None,
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-02T00:00:00'
            }
        }
        
        todo_model.table = MagicMock()
        todo_model.table.update_item.return_value = mock_response
        
        result = todo_model.mark_completed('todo-123', True)
        
        assert result['completed'] is True
        assert result['updated_at'] == '2023-01-02T00:00:00'

    def test_create_todo_with_defaults(self):
        """Test todo creation with default values."""
        todo_model = DynamoDBTodo()
        
        # Mock the table and uuid/datetime
        todo_model.table = MagicMock()
        
        with patch('src.models.dynamodb_todo.uuid.uuid4') as mock_uuid, \
             patch('src.models.dynamodb_todo.datetime') as mock_datetime:
            
            mock_uuid.return_value.__str__ = MagicMock(return_value='test-id')
            mock_datetime.utcnow.return_value.isoformat.return_value = '2023-01-01T00:00:00'
            
            result = todo_model.create_todo(
                user_id='user-123',
                title='Simple Todo'
                # Using defaults for description, priority, due_date
            )
            
            assert result['description'] == ''
            assert result['priority'] == 'medium'
            assert result['due_date'] is None
            assert result['completed'] is False
