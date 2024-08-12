"""
Celery tasks for synchronizing data between Google Drive and Pinecone.

This module defines Celery tasks that handle the synchronization process
between a user's Google Drive and the Pinecone vector database. It includes
tasks for both full and incremental syncs.
"""
from celery import shared_task
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.sync.sync_service import SyncService
from app.services.google_drive.core import DriveCore
from datetime import datetime, timezone
import logging
import redis
from config import Config
import json

logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)

@shared_task(name='tasks.sync_tasks.sync_drive_to_pinecone')
def sync_drive_to_pinecone(user_id):
    """
    Celery task to synchronize a user's Google Drive with Pinecone.

    This task retrieves the user's credentials, creates a DrivePineconeSync
    service, and performs either a full or incremental sync based on the
    last sync time. It then updates the last sync time for the user.

    Args:
        user_id (str): The ID of the user whose drive is to be synced.

    Returns:
        dict: A message indicating the completion of the sync process,
              or an error message if the user is not found or an error occurs.
    """
    logger.info(f"Starting sync for user_id: {user_id}")

    try:
        # Retrieve user credentials from Redis
        credentials_json = redis_client.get(f'user:{user_id}:token')
        if not credentials_json:
            logger.error(f"Credentials not found for user {user_id}")
            return {"error": f"Credentials not found for user {user_id}"}

        credentials = json.loads(credentials_json)
        drive_core = DriveCore(credentials)
        sync_service = DrivePineconeSync(user_id, drive_core)
        
        # Get last sync time from Redis
        last_sync_time = redis_client.get(f'user:{user_id}:last_sync_time')
        if last_sync_time:
            logger.info(f"Performing incremental sync for user {user_id}")
            sync_service.incremental_sync(datetime.fromisoformat(last_sync_time))
        else:
            logger.info(f"Performing full sync for user {user_id}")
            sync_service.full_sync()
        
        # Update last sync time
        new_last_sync_time = datetime.now(timezone.utc).isoformat()
        redis_client.set(f'user:{user_id}:last_sync_time', new_last_sync_time)

        # Update sync status
        SyncService.update_last_sync_time(user_id)

        logger.info(f"Sync completed for user {user_id}")
        return {"message": f"Sync completed for user {user_id}"}
    
    except Exception as e:
        logger.error(f"Error during sync for user {user_id}: {str(e)}")
        return {"error": f"Sync failed for user {user_id}: {str(e)}"}