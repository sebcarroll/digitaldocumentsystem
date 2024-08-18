"""
This module provides utility functions for Google Drive operations.

It includes functions for retrieving DriveCore instances based on user data stored in the session.
"""

import logging
from flask import session, has_request_context
from google.oauth2.credentials import Credentials
from app.services.google_drive.core import DriveCore

# Set up logging
logger = logging.getLogger(__name__)

def get_drive_core():
    """
    Retrieve a DriveCore instance based on credentials stored in the session.

    This function checks for the presence of a user_id and credentials in the current Flask session,
    and creates a DriveCore instance.

    Returns:
        DriveCore: An instance of DriveCore initialized with the user's credentials.

    Raises:
        ValueError: If no user_id or credentials are found in the session.
        Exception: For any other unexpected errors during DriveCore initialization.
    """
    logger.debug("Entering get_drive_core function")
    
    if not has_request_context():
        logger.error("No request context")
        raise RuntimeError("No request context")

    logger.debug(f"Session contents: {session}")
    
    user_id = session.get('user_id')
    if not user_id:
        logger.error("No user_id found in session")
        raise ValueError("User not authenticated")
    
    credentials = session.get('credentials')
    if not credentials:
        logger.error(f"No credentials found in session for user {user_id}")
        raise ValueError("User credentials not found")

    logger.debug(f"Credentials retrieved from session for user {user_id}")
    
    drive_core = DriveCore(Credentials.from_authorized_user_info(credentials))
    logger.info("DriveCore instance created successfully")
    return drive_core