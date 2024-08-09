import logging
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.google_drive.google_drive_service import GoogleDriveService
from app.services.google_drive.core import DriveCore
from app.services.user.user_service import UserService
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SyncService:
    @staticmethod
    def sync_user_drive(user_id):
        logger.info(f"Attempting to sync for user_id: {user_id}")

        user_service = UserService()
        user_data = user_service.get_user(user_id)

        if not user_data:
            logger.error("User not authenticated or user_id missing")
            return {"error": "User not authenticated or user_id missing"}

        credentials = user_data.get('credentials')

        if not credentials:
            logger.error("Credentials missing")
            return {"error": "Credentials missing"}

        # Validate credentials format
        if not isinstance(credentials, dict) or \
           not all(key in credentials for key in ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']):
            logger.error("Invalid credentials format")
            return {"error": "Invalid credentials format"}

        try:
            drive_core = DriveCore(credentials)
            drive_service = GoogleDriveService(drive_core)
            sync_service = DrivePineconeSync(user_id, drive_service)
            
            last_sync_time = user_data.get('last_sync_time')

            if last_sync_time:
                logger.info(f"Performing incremental sync from {last_sync_time}")
                sync_service.incremental_sync(last_sync_time)
            else:
                logger.info("Performing full sync")
                sync_service.full_sync()
            
            new_sync_time = datetime.now(timezone.utc)
            user_service.update_last_sync_time(user_id, new_sync_time.isoformat())
            logger.info(f"Sync completed successfully. New sync time: {new_sync_time.isoformat()}")
            
            return {"message": "Sync completed successfully"}
        except ValueError as e:
            logger.error(f"Invalid user or credentials: {str(e)}")
            return {"error": "Invalid credentials format"}
        except Exception as e:
            logger.exception(f"Sync failed: {str(e)}")
            return {"error": f"Sync failed: {str(e)}"}