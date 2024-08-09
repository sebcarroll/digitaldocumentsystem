import json
from google.oauth2.credentials import Credentials
from app.services.google_drive.core import DriveCore

class UserService:
    @staticmethod
    def get_user(user_id):
        try:
            with open(f'tokens/{user_id}.json', 'r') as token_file:
                user_data = json.load(token_file)
            return user_data
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            raise ValueError(f"Corrupted token file for user {user_id}")

    @staticmethod
    def update_last_sync_time(user_id, last_sync_time):
        try:
            with open(f'tokens/{user_id}.json', 'r+') as token_file:
                user_data = json.load(token_file)
                user_data['last_sync_time'] = last_sync_time
                token_file.seek(0)
                json.dump(user_data, token_file, indent=2)
                token_file.truncate()
        except FileNotFoundError:
            raise ValueError(f"No token file found for user {user_id}")
        except json.JSONDecodeError:
            raise ValueError(f"Corrupted token file for user {user_id}")

    @staticmethod
    def get_drive_core(user_id):
        try:
            with open(f'tokens/{user_id}.json', 'r') as token_file:
                credentials_data = json.load(token_file)
            return DriveCore(credentials_data)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            raise ValueError(f"Corrupted token file for user {user_id}")