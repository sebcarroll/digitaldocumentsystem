from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.google_drive.google_drive_service import GoogleDriveService
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone

class SyncService:
    @staticmethod
    def sync_user_drive(session):
        if 'credentials' not in session or 'user_id' not in session:
            return {"error": "User not authenticated or user_id missing"}

        credentials_dict = session['credentials']
        user_id = session['user_id']
        
        if not isinstance(credentials_dict, dict):
            return {"error": "Invalid credentials format"}

        try:
            drive_service = GoogleDriveService(credentials_dict)
            sync_service = DrivePineconeSync(user_id, drive_service)
            
            last_sync_time = session.get('last_sync_time')
            if last_sync_time:
                sync_service.incremental_sync(last_sync_time)
            else:
                sync_service.full_sync()
            
            session['last_sync_time'] = datetime.now(timezone.utc).isoformat()
            
            return {"message": "Sync completed successfully"}
        except Exception as e:
            return {"error": f"Sync failed: {str(e)}"}