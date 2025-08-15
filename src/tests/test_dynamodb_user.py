"""
Tests for DynamoDB User model.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from botocore.exceptions import ClientError

from src.models.dynamodb_user import DynamoDBUser


class TestDynamoDBUser:
    """Test class for DynamoDB User model."""

    @patch('src.models.dynamodb_user.boto3')
    def test_init_local_environment(self, mock_boto3):
        """Test initialization with local DynamoDB environment."""
        # Mock environment variable for local DynamoDB
        with patch.dict(os.environ, {'DYNAMODB_LOCAL': 'true', 'DYNAMODB_TABLE': 'test-users'}):
            mock_resource = Mock()
            mock_table = Mock()
            mock_resource.Table.return_value = mock_table
            mock_boto3.resource.return_value = mock_resource
            
            user_model = DynamoDBUser()
            
            # Verify local DynamoDB configuration
            mock_boto3.resource.assert_called_once_with(
                'dynamodb',
                endpoint_url='http://localhost:8000',
                region_name='us-east-1',
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy'
            )
            assert user_model.table_name == 'test-users'
            assert user_model.table == mock_table

    @patch('src.models.dynamodb_user.boto3')
    def test_init_production_environment(self, mock_boto3):
        """Test initialization with production DynamoDB environment."""
        # Mock environment variables for production
        with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}, clear=True):
            mock_resource = Mock()
            mock_table = Mock()
            mock_resource.Table.return_value = mock_table
            mock_boto3.resource.return_value = mock_resource
            
            user_model = DynamoDBUser()
            
            # Verify production DynamoDB configuration
            mock_boto3.resource.assert_called_once_with('dynamodb', region_name='us-west-2')
            assert user_model.table_name == 'kelly-user-management-dev-users'  # default
            assert user_model.table == mock_table

    def test_to_dict_with_valid_item(self):
        """Test converting DynamoDB item to dictionary format."""
        user_model = DynamoDBUser()
        
        dynamo_item = {
            'id': '1234567890',
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-02T00:00:00',
            'is_active': True
        }
        
        result = user_model.to_dict(dynamo_item)
        
        expected = {
            'id': 1234567890,  # Should be converted to int
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-02T00:00:00',
            'is_active': True
        }
        
        assert result == expected

    def test_to_dict_with_empty_item(self):
        """Test converting empty DynamoDB item."""
        user_model = DynamoDBUser()
        
        result = user_model.to_dict({})
        assert result == {}
        
        result = user_model.to_dict(None)
        assert result == {}

    def test_to_dict_with_missing_fields(self):
        """Test converting DynamoDB item with missing fields."""
        user_model = DynamoDBUser()
        
        incomplete_item = {
            'id': '123',
            'username': 'testuser'
            # Missing other fields
        }
        
        result = user_model.to_dict(incomplete_item)
        
        expected = {
            'id': 123,
            'username': 'testuser',
            'email': '',
            'first_name': '',
            'last_name': '',
            'created_at': '',
            'updated_at': None,
            'is_active': True
        }
        
        assert result == expected

    @patch('src.models.dynamodb_user.uuid.uuid4')
    @patch('src.models.dynamodb_user.datetime')
    def test_create_user_success(self, mock_datetime, mock_uuid):
        """Test successful user creation."""
        # Setup mocks
        mock_uuid.return_value.int = 123456789012345
        mock_datetime.utcnow.return_value.isoformat.return_value = '2023-01-01T00:00:00'
        
        user_model = DynamoDBUser()
        user_model.table = Mock()
        user_model.get_user_by_username = Mock(return_value=None)
        user_model.get_user_by_email = Mock(return_value=None)
        
        # Test user creation
        result = user_model.create_user(
            username='newuser',
            email='new@example.com',
            first_name='New',
            last_name='User'
        )
        
        # Verify DynamoDB put_item was called
        expected_item = {
            'id': '1234567890',
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': None,
            'is_active': True
        }
        user_model.table.put_item.assert_called_once_with(Item=expected_item)
        
        # Verify returned user data
        assert result['username'] == 'newuser'
        assert result['email'] == 'new@example.com'
        assert result['first_name'] == 'New'
        assert result['last_name'] == 'User'
        assert result['is_active'] is True

    def test_create_user_duplicate_username(self):
        """Test user creation with duplicate username."""
        user_model = DynamoDBUser()
        user_model.get_user_by_username = Mock(return_value={'id': 1, 'username': 'existinguser'})
        user_model.get_user_by_email = Mock(return_value=None)
        
        with pytest.raises(ValueError, match="Username already exists"):
            user_model.create_user(
                username='existinguser',
                email='new@example.com',
                first_name='New',
                last_name='User'
            )

    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        user_model = DynamoDBUser()
        user_model.get_user_by_username = Mock(return_value=None)
        user_model.get_user_by_email = Mock(return_value={'id': 1, 'email': 'existing@example.com'})
        
        with pytest.raises(ValueError, match="Email already exists"):
            user_model.create_user(
                username='newuser',
                email='existing@example.com',
                first_name='New',
                last_name='User'
            )

    def test_create_user_client_error(self):
        """Test user creation with DynamoDB ClientError."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        user_model.get_user_by_username = Mock(return_value=None)
        user_model.get_user_by_email = Mock(return_value=None)
        
        # Mock ClientError
        error_response = {'Error': {'Code': 'ValidationException', 'Message': 'Invalid input'}}
        user_model.table.put_item.side_effect = ClientError(error_response, 'PutItem')
        
        with pytest.raises(Exception, match="Failed to create user"):
            user_model.create_user(
                username='newuser',
                email='new@example.com',
                first_name='New',
                last_name='User'
            )

    def test_get_all_users_success(self):
        """Test successful retrieval of all users."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        # Mock DynamoDB response
        mock_response = {
            'Items': [
                {'id': '1', 'username': 'user1', 'email': 'user1@example.com'},
                {'id': '2', 'username': 'user2', 'email': 'user2@example.com'}
            ]
        }
        user_model.table.scan.return_value = mock_response
        
        # Mock to_dict method
        user_model.to_dict = Mock(side_effect=lambda x: x)
        
        result = user_model.get_all_users()
        
        user_model.table.scan.assert_called_once()
        assert len(result) == 2
        assert user_model.to_dict.call_count == 2

    def test_get_all_users_with_pagination(self):
        """Test retrieval of all users with pagination."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        # Mock DynamoDB responses with pagination
        first_response = {
            'Items': [{'id': '1', 'username': 'user1'}],
            'LastEvaluatedKey': {'id': '1'}
        }
        second_response = {
            'Items': [{'id': '2', 'username': 'user2'}]
            # No LastEvaluatedKey, indicating end of pagination
        }
        
        user_model.table.scan.side_effect = [first_response, second_response]
        user_model.to_dict = Mock(side_effect=lambda x: x)
        
        result = user_model.get_all_users()
        
        # Verify pagination calls
        assert user_model.table.scan.call_count == 2
        user_model.table.scan.assert_any_call()
        user_model.table.scan.assert_any_call(ExclusiveStartKey={'id': '1'})
        
        assert len(result) == 2

    def test_get_all_users_client_error(self):
        """Test get_all_users with DynamoDB ClientError."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        error_response = {'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}}
        user_model.table.scan.side_effect = ClientError(error_response, 'Scan')
        
        with pytest.raises(Exception, match="Failed to get users"):
            user_model.get_all_users()

    def test_get_user_by_id_success(self):
        """Test successful retrieval of user by ID."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        mock_response = {
            'Item': {'id': '123', 'username': 'testuser', 'email': 'test@example.com'}
        }
        user_model.table.get_item.return_value = mock_response
        user_model.to_dict = Mock(return_value={'id': 123, 'username': 'testuser'})
        
        result = user_model.get_user_by_id('123')
        
        user_model.table.get_item.assert_called_once_with(Key={'id': '123'})
        user_model.to_dict.assert_called_once_with(mock_response['Item'])
        assert result == {'id': 123, 'username': 'testuser'}

    def test_get_user_by_id_not_found(self):
        """Test retrieval of non-existent user by ID."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        mock_response = {}  # No 'Item' key means user not found
        user_model.table.get_item.return_value = mock_response
        
        result = user_model.get_user_by_id('999')
        
        assert result is None

    def test_get_user_by_id_client_error(self):
        """Test get_user_by_id with DynamoDB ClientError."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        error_response = {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Table not found'}}
        user_model.table.get_item.side_effect = ClientError(error_response, 'GetItem')
        
        with pytest.raises(Exception, match="Failed to get user"):
            user_model.get_user_by_id('123')

    def test_get_user_by_username_success(self):
        """Test successful retrieval of user by username."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        mock_response = {
            'Items': [{'id': '123', 'username': 'testuser', 'email': 'test@example.com'}]
        }
        user_model.table.query.return_value = mock_response
        user_model.to_dict = Mock(return_value={'id': 123, 'username': 'testuser'})
        
        result = user_model.get_user_by_username('testuser')
        
        user_model.table.query.assert_called_once_with(
            IndexName='username-index',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': 'testuser'}
        )
        assert result == {'id': 123, 'username': 'testuser'}

    def test_get_user_by_username_not_found(self):
        """Test retrieval of non-existent user by username."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        mock_response = {'Items': []}  # Empty list means user not found
        user_model.table.query.return_value = mock_response
        
        result = user_model.get_user_by_username('nonexistent')
        
        assert result is None

    def test_get_user_by_email_success(self):
        """Test successful retrieval of user by email."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        mock_response = {
            'Items': [{'id': '123', 'username': 'testuser', 'email': 'test@example.com'}]
        }
        user_model.table.query.return_value = mock_response
        user_model.to_dict = Mock(return_value={'id': 123, 'email': 'test@example.com'})
        
        result = user_model.get_user_by_email('test@example.com')
        
        user_model.table.query.assert_called_once_with(
            IndexName='email-index',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': 'test@example.com'}
        )
        assert result == {'id': 123, 'email': 'test@example.com'}

    def test_get_user_by_email_client_error(self):
        """Test get_user_by_email with DynamoDB ClientError."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        error_response = {'Error': {'Code': 'ValidationException', 'Message': 'Invalid GSI'}}
        user_model.table.query.side_effect = ClientError(error_response, 'Query')
        
        with pytest.raises(Exception, match="Failed to get user"):
            user_model.get_user_by_email('test@example.com')

    @patch('src.models.dynamodb_user.datetime')
    def test_update_user_success(self, mock_datetime):
        """Test successful user update."""
        mock_datetime.utcnow.return_value.isoformat.return_value = '2023-01-02T00:00:00'
        
        user_model = DynamoDBUser()
        user_model.table = Mock()
        user_model.get_user_by_id = Mock(return_value={'id': 123, 'email': 'old@example.com'})
        user_model.get_user_by_email = Mock(return_value=None)  # No conflict
        
        # Mock update response
        mock_response = {
            'Attributes': {
                'id': '123',
                'username': 'testuser',
                'email': 'new@example.com',
                'first_name': 'Updated',
                'last_name': 'User',
                'updated_at': '2023-01-02T00:00:00'
            }
        }
        user_model.table.update_item.return_value = mock_response
        user_model.to_dict = Mock(return_value={'id': 123, 'email': 'new@example.com'})
        
        result = user_model.update_user('123', email='new@example.com', first_name='Updated')
        
        # Verify update call
        user_model.table.update_item.assert_called_once()
        update_call = user_model.table.update_item.call_args
        
        assert update_call[1]['Key'] == {'id': '123'}
        assert 'email = :email' in update_call[1]['UpdateExpression']
        assert 'first_name = :first_name' in update_call[1]['UpdateExpression']
        assert update_call[1]['ExpressionAttributeValues'][':email'] == 'new@example.com'
        assert update_call[1]['ExpressionAttributeValues'][':first_name'] == 'Updated'
        
        assert result == {'id': 123, 'email': 'new@example.com'}

    def test_update_user_not_found(self):
        """Test updating non-existent user."""
        user_model = DynamoDBUser()
        user_model.get_user_by_id = Mock(return_value=None)
        
        with pytest.raises(ValueError, match="User not found"):
            user_model.update_user('999', first_name='Updated')

    def test_update_user_email_conflict(self):
        """Test updating user with conflicting email."""
        user_model = DynamoDBUser()
        user_model.get_user_by_id = Mock(return_value={'id': 123, 'email': 'old@example.com'})
        user_model.get_user_by_email = Mock(return_value={'id': 456, 'email': 'conflict@example.com'})
        
        with pytest.raises(ValueError, match="Email already exists"):
            user_model.update_user('123', email='conflict@example.com')

    def test_update_user_same_email(self):
        """Test updating user with their own email (should not conflict)."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        
        existing_user = {'id': 123, 'email': 'same@example.com'}
        user_model.get_user_by_id = Mock(return_value=existing_user)
        user_model.get_user_by_email = Mock(return_value=existing_user)  # Same user
        
        mock_response = {'Attributes': {'id': '123', 'email': 'same@example.com'}}
        user_model.table.update_item.return_value = mock_response
        user_model.to_dict = Mock(return_value={'id': 123})
        
        # Should not raise an error
        result = user_model.update_user('123', email='same@example.com', first_name='Updated')
        assert result == {'id': 123}

    def test_update_user_client_error(self):
        """Test update_user with DynamoDB ClientError."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        user_model.get_user_by_id = Mock(return_value={'id': 123, 'email': 'test@example.com'})
        
        error_response = {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'Condition failed'}}
        user_model.table.update_item.side_effect = ClientError(error_response, 'UpdateItem')
        
        with pytest.raises(Exception, match="Failed to update user"):
            user_model.update_user('123', first_name='Updated')

    def test_delete_user_success(self):
        """Test successful user deletion."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        user_model.get_user_by_id = Mock(return_value={'id': 123, 'username': 'testuser'})
        
        result = user_model.delete_user('123')
        
        user_model.table.delete_item.assert_called_once_with(Key={'id': '123'})
        assert result is True

    def test_delete_user_not_found(self):
        """Test deleting non-existent user."""
        user_model = DynamoDBUser()
        user_model.get_user_by_id = Mock(return_value=None)
        
        with pytest.raises(ValueError, match="User not found"):
            user_model.delete_user('999')

    def test_delete_user_client_error(self):
        """Test delete_user with DynamoDB ClientError."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        user_model.get_user_by_id = Mock(return_value={'id': 123, 'username': 'testuser'})
        
        error_response = {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Item not found'}}
        user_model.table.delete_item.side_effect = ClientError(error_response, 'DeleteItem')
        
        with pytest.raises(Exception, match="Failed to delete user"):
            user_model.delete_user('123')

    def test_invalid_update_fields(self):
        """Test updating user with invalid fields (should be ignored)."""
        user_model = DynamoDBUser()
        user_model.table = Mock()
        user_model.get_user_by_id = Mock(return_value={'id': 123, 'email': 'test@example.com'})
        
        mock_response = {'Attributes': {'id': '123'}}
        user_model.table.update_item.return_value = mock_response
        user_model.to_dict = Mock(return_value={'id': 123})
        
        # Test with invalid field - should only update valid fields
        result = user_model.update_user('123', invalid_field='should_be_ignored', first_name='Valid')
        
        update_call = user_model.table.update_item.call_args
        update_expression = update_call[1]['UpdateExpression']
        
        # Should include first_name but not invalid_field
        assert 'first_name = :first_name' in update_expression
        assert 'invalid_field' not in update_expression
        assert result == {'id': 123}
