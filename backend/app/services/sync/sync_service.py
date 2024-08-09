import logging
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.google_drive.google_drive_service import GoogleDriveService
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
class SyncService:
    @staticmethod
    def sync_user_drive(session):
        if 'credentials' not in session or 'user_id' not in session:
            logger.error("Missing credentials or user_id in session")
            return {"error": "User not authenticated or user_id missing"}

        credentials_data = session['credentials']
        user_id = session['user_id']
        
        logger.info(f"Attempting to sync for user_id: {user_id}")
        logger.debug(f"Credentials type: {type(credentials_data)}")
        logger.debug(f"Credentials data keys: {credentials_data.keys() if isinstance(credentials_data, dict) else 'Not a dict'}")

        if not isinstance(credentials_data, (dict, Credentials)):
            logger.error(f"Invalid credentials format: {type(credentials_data)}")
            return {"error": "Invalid credentials format"}

        try:
            drive_service = GoogleDriveService(credentials_data)
            sync_service = DrivePineconeSync(user_id, drive_service)
            
            last_sync_time = session.get('last_sync_time')
            if last_sync_time:
                logger.info(f"Performing incremental sync from {last_sync_time}")
                sync_service.incremental_sync(last_sync_time)
            else:
                logger.info("Performing full sync")
                sync_service.full_sync()
            
            new_sync_time = datetime.now(timezone.utc).isoformat()
            session['last_sync_time'] = new_sync_time
            logger.info(f"Sync completed successfully. New sync time: {new_sync_time}")
            
            return {"message": "Sync completed successfully"}
        except Exception as e:
            logger.exception(f"Sync failed: {str(e)}")
            return {"error": f"Sync failed: {str(e)}"}