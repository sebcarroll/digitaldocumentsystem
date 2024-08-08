from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone

class SyncService:
    @staticmethod
    def sync_user_drive(session):
        if 'credentials' not in session:
            return {"error": "User not authenticated"}

        credentials = Credentials(**session['credentials'])
        user_id = session.get('user_id')
        
        sync_service = DrivePineconeSync(user_id, credentials)
        
        last_sync_time = session.get('last_sync_time')
        if last_sync_time:
            sync_service.incremental_sync(last_sync_time)
        else:
            sync_service.full_sync()
        
        session['last_sync_time'] = datetime.now(timezone.utc).isoformat()
        
        return {"message": "Sync completed successfully"}