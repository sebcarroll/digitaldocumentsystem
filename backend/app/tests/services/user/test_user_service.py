"""
Unit tests for the UserService class, which interacts with Redis to store and retrieve user data, including OAuth2 tokens.

This module includes tests for the following methods:
- get_user: Retrieves user data from Redis based on the user ID.
- update_last_sync_time: Updates the last sync time for a user in Redis.
- get_drive_core: Retrieves a DriveCore instance based on stored credentials.

Each test mocks the Redis interactions to avoid dependency on an actual Redis instance.
"""

# import pytest
# from unittest.mock import patch, MagicMock
# from app.services.user.user_service import UserService
# import json
# 
# @pytest.fixture
# def mock_redis():
#     """
#     Fixture to mock the Redis client.
# 
#     This fixture patches the redis.StrictRedis class to return a mock instance,
#     allowing control over Redis behavior in the tests.
# 
#     Yields:
#         MagicMock: A mocked instance of the Redis client.
#     """
#     with patch('redis.StrictRedis') as mock_redis:
#         yield mock_redis
# 
# def test_get_user(mock_redis):
#     """
#     Test that get_user retrieves and returns the correct user data from Redis.
# 
#     Mocks the Redis get method to return a serialized JSON string representing the user's data.
#     Asserts that the returned data contains the correct user_id and credentials.
# 
#     Args:
#         mock_redis (MagicMock): The mocked Redis client.
#     """
#     # Mock the Redis `get` method
#     mock_redis_instance = mock_redis.from_url.return_value
#     mock_redis_instance.get.return_value = json.dumps({
#         'user_id': 'test_user_id',
#         'credentials': {
#             'token': 'fake_token',
#             'refresh_token': 'fake_refresh_token',
#             'token_uri': 'https://oauth2.googleapis.com/token',
#             'client_id': 'fake_client_id',
#             'client_secret': 'fake_client_secret',
#             'scopes': ['https://www.googleapis.com/auth/drive']
#         }
#     })
# 
#     # Create an instance of UserService
#     user_service = UserService()
# 
#     # Call get_user
#     user = user_service.get_user('test_user_id')
# 
#     # Assert that the user data is correctly returned
#     assert user['user_id'] == 'test_user_id'
#     assert 'credentials' in user
# 
#     # Assert that Redis `get` method was called with the correct key
#     mock_redis_instance.get.assert_called_once_with('user:test_user_id:token')
# 
# def test_get_user_not_found(mock_redis):
#     """
#     Test that get_user returns None when the user is not found in Redis.
# 
#     Mocks the Redis get method to return None, simulating a missing user.
#     Asserts that the get_user method returns None.
# 
#     Args:
#         mock_redis (MagicMock): The mocked Redis client.
#     """
#     # Mock the Redis `get` method to return None
#     mock_redis_instance = mock_redis.from_url.return_value
#     mock_redis_instance.get.return_value = None
# 
#     # Create an instance of UserService
#     user_service = UserService()
# 
#     # Call get_user
#     user = user_service.get_user('test_user_id')
# 
#     # Assert that the user data is None
#     assert user is None
# 
#     # Assert that Redis `get` method was called with the correct key
#     mock_redis_instance.get.assert_called_once_with('user:test_user_id:token')
# 
# def test_update_last_sync_time(mock_redis):
#     """
#     Test that update_last_sync_time updates the last sync time for the user in Redis.
# 
#     Mocks the Redis get method to return existing user data and the set method to capture the update.
#     Verifies that the updated data contains the correct last_sync_time.
# 
#     Args:
#         mock_redis (MagicMock): The mocked Redis client.
#     """
#     # Mock the Redis `get` and `set` methods
#     mock_redis_instance = mock_redis.from_url.return_value
#     mock_redis_instance.get.return_value = json.dumps({
#         'user_id': 'test_user_id',
#         'credentials': {
#             'token': 'fake_token',
#             'refresh_token': 'fake_refresh_token',
#             'token_uri': 'https://oauth2.googleapis.com/token',
#             'client_id': 'fake_client_id',
#             'client_secret': 'fake_client_secret',
#             'scopes': ['https://www.googleapis.com/auth/drive']
#         }
#     })
# 
#     # Create an instance of UserService
#     user_service = UserService()
# 
#     # Call update_last_sync_time
#     user_service.update_last_sync_time('test_user_id', '2023-01-01T00:00:00')
# 
#     # Assert that Redis `get` method was called with the correct key
#     mock_redis_instance.get.assert_called_once_with('user:test_user_id:token')
# 
#     # Assert that Redis `set` method was called with the correct key and value
#     updated_user_data = json.loads(mock_redis_instance.set.call_args[0][1])
#     assert updated_user_data['last_sync_time'] == '2023-01-01T00:00:00'
#     mock_redis_instance.set.assert_called_once_with('user:test_user_id:token', mock_redis_instance.set.call_args[0][1])
# 
# def test_update_last_sync_time_user_not_found(mock_redis):
#     """
#     Test that update_last_sync_time raises a ValueError when the user is not found.
# 
#     Mocks the Redis get method to return None, simulating a missing user.
#     Asserts that update_last_sync_time raises a ValueError with an appropriate message.
# 
#     Args:
#         mock_redis (MagicMock): The mocked Redis client.
#     """
#     # Mock the Redis `get` method to return None
#     mock_redis_instance = mock_redis.from_url.return_value
#     mock_redis_instance.get.return_value = None
# 
#     # Create an instance of UserService
#     user_service = UserService()
# 
#     # Assert that an exception is raised when updating last sync time for a non-existent user
#     with pytest.raises(ValueError, match="No token data found for user test_user_id"):
#         user_service.update_last_sync_time('test_user_id', '2023-01-01T00:00:00')
