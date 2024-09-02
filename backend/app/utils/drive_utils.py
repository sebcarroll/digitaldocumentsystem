"""
This module provides utility functions for Google Drive operations.

It includes functions for retrieving DriveCore instances based on user data stored in Redis.
"""

import json
import redis
from google.oauth2.credentials import Credentials
from app.services.google_drive.core import DriveCore
from config import Config

# Initialize Redis client
redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)

def get_drive_core(session):
    """
    Retrieve a DriveCore instance based on credentials stored in Redis.

    This function checks for the presence of a user_id in the provided session,
    retrieves the corresponding credentials from Redis, and creates a DriveCore instance.

    Args:
        session (dict): The session object containing user_id.

    Returns:
        DriveCore: An instance of DriveCore initialized with the user's credentials.

    Raises:
        ValueError: If no user_id is found in the session or no credentials are found in Redis.
        TypeError: If the credentials in Redis are of an unexpected type.
        Exception: For any other unexpected errors during DriveCore initialization.
    """
    # Check for user_id in session
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError("User not authenticated")
    
    try:
        # Retrieve credentials from Redis
        credentials_json = redis_client.get(f'user:{user_id}:token')
        if not credentials_json:
            raise ValueError("User credentials not found")

        # Parse credentials JSON
        credentials_dict = json.loads(credentials_json)
        
        # Create and return DriveCore instance
        drive_core = DriveCore(credentials_dict)
        return drive_core
    
    except json.JSONDecodeError as e:
        # Handle invalid JSON format
        raise ValueError(f"Invalid credentials format in storage")
    except TypeError as e:
        # Handle unexpected credential type
        raise
    except Exception as e:
        # Handle any other unexpected errors
        raise ValueError(f"Failed to initialize DriveCore: {str(e)}")