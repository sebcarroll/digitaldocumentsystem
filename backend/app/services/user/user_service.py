from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class UserService:
    @staticmethod
    def get_user(user_id):
        # Fetch user info from Google
        credentials = Credentials.from_authorized_user_file(f'tokens/{user_id}.json')
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        return {
            'id': user_id,
            'email': user_info['email'],
            'name': user_info['name'],
            'credentials': credentials.to_json()
        }

    @staticmethod
    def update_last_sync_time(user_id, last_sync_time):
        # Since we're not using a database, we'll store this in the user's token file
        credentials = Credentials.from_authorized_user_file(f'tokens/{user_id}.json')
        credentials.last_sync_time = last_sync_time
        with open(f'tokens/{user_id}.json', 'w') as token:
            token.write(credentials.to_json())