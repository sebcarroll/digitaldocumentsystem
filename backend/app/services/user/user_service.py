"""
This module provides a UserService class for managing user data and credentials.

It interacts with a Redis database to store and retrieve user tokens and
provides methods to create DriveCore instances for Google Drive operations.
"""

import redis
import json
import logging
from app.services.google_drive.core import DriveCore
from config import Config

logger = logging.getLogger(__name__)

class UserService:
    """
    A service class for managing user data and credentials.

    This class provides methods to interact with a Redis database for storing
    and retrieving user tokens, updating sync times, and creating DriveCore
    instances for Google Drive operations.
    """

    def __init__(self):
        """
        Initialize the UserService with a Redis connection.

        Raises:
            redis.ConnectionError: If unable to connect to Redis.
        """
        try:
            self.redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)
            self.redis_client.ping()  # Test the connection
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    def get_user(self, user_id):
        """
        Retrieve user data from Redis.

        Args:
            user_id (str): The ID of the user.

        Returns:
            dict: User data if found, None otherwise.

        Raises:
            ValueError: If the token data is corrupted.
            redis.RedisError: If there's an issue with the Redis operation.
        """
        logger.debug(f"Attempting to get user data for user_id: {user_id}")
        try:
            user_data = self.redis_client.get(f'user:{user_id}:token')
            if user_data:
                logger.info(f"User data found for user_id: {user_id}")
                return json.loads(user_data)
            logger.warning(f"No user data found for user_id: {user_id}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Corrupted token data for user {user_id}")
            raise ValueError(f"Corrupted token data for user {user_id}")
        except redis.RedisError as e:
            logger.error(f"Redis error when getting user data: {str(e)}")
            raise

    def update_last_sync_time(self, user_id, last_sync_time):
        """
        Update the last synchronization time for a user.

        Args:
            user_id (str): The ID of the user.
            last_sync_time (str): The timestamp of the last synchronization.

        Raises:
            ValueError: If no token data is found for the user or if the token data is corrupted.
            redis.RedisError: If there's an issue with the Redis operation.
        """
        logger.debug(f"Updating last sync time for user_id: {user_id}")
        try:
            user_data = self.get_user(user_id)
            if not user_data:
                logger.error(f"No token data found for user {user_id}")
                raise ValueError(f"No token data found for user {user_id}")

            user_data['last_sync_time'] = last_sync_time
            self.redis_client.set(f'user:{user_id}:token', json.dumps(user_data))
            logger.info(f"Last sync time updated for user_id: {user_id}")
        except json.JSONDecodeError:
            logger.error(f"Corrupted token data for user {user_id}")
            raise ValueError(f"Corrupted token data for user {user_id}")
        except redis.RedisError as e:
            logger.error(f"Redis error when updating last sync time: {str(e)}")
            raise

    def get_drive_core(self, user_id):
        """
        Create and return a DriveCore instance for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            DriveCore: An instance of DriveCore for the user.

        Raises:
            ValueError: If no credentials are found for the user or if the credential data is invalid.
            Exception: For any other unexpected errors.
        """
        logger.debug(f"Attempting to get DriveCore for user_id: {user_id}")
        try:
            credentials_data = self.get_user(user_id)
            if not credentials_data:
                logger.error(f"No credentials found for user {user_id}")
                raise ValueError(f"No credentials found for user {user_id}")
            
            # Validate credential data structure
            required_keys = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
            if not all(key in credentials_data for key in required_keys):
                logger.error(f"Invalid credential data structure for user {user_id}")
                raise ValueError(f"Invalid credential data structure for user {user_id}")
            
            drive_core = DriveCore(credentials_data)
            logger.info(f"DriveCore created successfully for user_id: {user_id}")
            return drive_core
        except json.JSONDecodeError:
            logger.error(f"Corrupted token data for user {user_id}")
            raise ValueError(f"Corrupted token data for user {user_id}")
        except Exception as e:
            logger.exception(f"Unexpected error when getting DriveCore for user {user_id}: {str(e)}")
            raise