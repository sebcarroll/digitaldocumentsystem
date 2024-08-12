"""
This module provides a SyncService class for synchronizing Google Drive contents with a Pinecone vector database.

It uses DriveCore to interact with Google Drive and coordinates the synchronization process 
using DrivePineconeSync services.
"""

import logging
from datetime import datetime, timezone
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.google_drive.google_drive_service import GoogleDriveService
from app.services.google_drive.core import DriveCore
import redis
import json
from config import Config

logger = logging.getLogger(__name__)

class SyncService:
    """
    A service class for synchronizing user's Google Drive with Pinecone database.

    This class provides methods to perform full or incremental synchronization
    of a user's Google Drive contents with a Pinecone vector database.
    """

    @staticmethod
    def sync_user_drive(user_id):
        """
        Synchronize a user's Google Drive with Pinecone database.

        This method retrieves user credentials, initializes necessary services,
        and performs either a full or incremental sync based on the last sync time.

        Args:
            user_id (str): The ID of the user whose drive is to be synced.

        Returns:
            dict: A dictionary containing a success message or error information.
        """
        logger.info(f"Attempting to sync for user_id: {user_id}")

        redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)

        # Retrieve credentials from Redis
        credentials_json = redis_client.get(f'user:{user_id}:token')
        last_sync_time = redis_client.get(f'user:{user_id}:last_sync_time')

        if not credentials_json:
            logger.error("Credentials missing")
            return {"error": "Credentials missing"}

        try:
            credentials = json.loads(credentials_json)
            logger.debug(f"Retrieved credentials for user: {user_id}")

            sync_service = DrivePineconeSync(user_id, credentials)
            
            if last_sync_time:
                logger.info(f"Performing incremental sync from {last_sync_time}")
                sync_result = sync_service.incremental_sync(datetime.fromisoformat(last_sync_time))
            else:
                logger.info("Performing full sync")
                sync_result = sync_service.full_sync()
            
            if sync_result:
                new_sync_time = datetime.now(timezone.utc)
                redis_client.set(f'user:{user_id}:last_sync_time', new_sync_time.isoformat())
                logger.info(f"Sync completed successfully. New sync time: {new_sync_time.isoformat()}")
                return {"message": "Sync completed successfully"}
            else:
                logger.error("Sync failed")
                return {"error": "Sync failed"}

        except json.JSONDecodeError as e:
            logger.error(f"Invalid credentials format: {str(e)}")
            return {"error": "Invalid credentials format"}
        except Exception as e:
            logger.exception(f"Sync failed: {str(e)}")
            return {"error": f"Sync failed: {str(e)}"}