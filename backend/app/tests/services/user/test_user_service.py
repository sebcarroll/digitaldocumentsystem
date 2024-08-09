import pytest
from unittest.mock import mock_open, patch, call
from app.services.user.user_service import UserService
from google.oauth2.credentials import Credentials
import json

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
    'credentials': {
        'token': 'fake_token',
        'refresh_token': 'fake_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'fake_client_id',
        'client_secret': 'fake_client_secret',
        'scopes': ['https://www.googleapis.com/auth/drive']
    },
    'user_id': 'test_user_id'
}))
def test_get_user(mock_file):
    user = UserService.get_user('test_user_id')
    assert user['user_id'] == 'test_user_id'
    assert 'credentials' in user

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
    'credentials': {
        'token': 'fake_token',
        'refresh_token': 'fake_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'fake_client_id',
        'client_secret': 'fake_client_secret',
        'scopes': ['https://www.googleapis.com/auth/drive']
    },
    'user_id': 'test_user_id'
}))
def test_update_last_sync_time(mock_file):
    UserService.update_last_sync_time('test_user_id', '2023-01-01T00:00:00')

    # Ensure write was called
    mock_file().write.assert_called()

    # Get all write calls
    write_calls = mock_file().write.call_args_list

    # Combine all written data
    written_data = ''.join(call[0][0] for call in write_calls)

    # Now parse the complete JSON string
    parsed_data = json.loads(written_data)

    # Perform assertions on the final written data
    assert parsed_data is not None
    assert 'last_sync_time' in parsed_data
    assert parsed_data['last_sync_time'] == '2023-01-01T00:00:00'