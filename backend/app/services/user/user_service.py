import redis
import json
from app.services.google_drive.core import DriveCore
from config import Config
class UserService:
    def __init__(self):
        self.redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)

    def get_user(self, user_id):
        try:
            user_data = self.redis_client.get(f'user:{user_id}:token')
            if user_data:
                return json.loads(user_data)
            return None
        except json.JSONDecodeError:
            raise ValueError(f"Corrupted token data for user {user_id}")

    def update_last_sync_time(self, user_id, last_sync_time):
        try:
            user_data = self.get_user(user_id)
            if not user_data:
                raise ValueError(f"No token data found for user {user_id}")

            user_data['last_sync_time'] = last_sync_time
            self.redis_client.set(f'user:{user_id}:token', json.dumps(user_data))
        except json.JSONDecodeError:
            raise ValueError(f"Corrupted token data for user {user_id}")

    def get_drive_core(self, user_id):
        try:
            credentials_data = self.get_user(user_id)
            if credentials_data:
                return DriveCore(credentials_data)
            return None
        except json.JSONDecodeError:
            raise ValueError(f"Corrupted token data for user {user_id}")

