"""
This module provides utility functions for Google Drive operations.

It includes functions for retrieving DriveCore instances based on user data stored in Redis.
"""

import logging
import json
import redis
from google.oauth2.credentials import Credentials
from app.services.google_drive.core import DriveCore
from config import Config
from app.services.user.user_service import UserService

# Set up logging
logger = logging.getLogger(__name__)

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
    logger.debug("Entering get_drive_core function")
    
    user_id = session.get('user_id')
    if not user_id:
        logger.error("No user_id found in session")
        raise ValueError("User not authenticated")
    
    try:
        user_service = UserService()
        user_data = user_service.get_user(user_id)
        if not user_data or 'credentials' not in user_data:
            logger.error(f"No credentials found in Redis for user {user_id}")
            raise ValueError("User credentials not found")

        credentials_dict = user_data['credentials']
        logger.debug(f"Credentials retrieved from Redis for user {user_id}")
        
        drive_core = DriveCore(credentials_dict)
        logger.info("DriveCore instance created successfully")
        return drive_core
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in Redis for user {user_id}: {str(e)}")
        raise ValueError(f"Invalid credentials format in storage")
    except TypeError as e:
        logger.error(f"TypeError in get_drive_core: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in get_drive_core: {str(e)}")
        raise ValueError(f"Failed to initialize DriveCore: {str(e)}")