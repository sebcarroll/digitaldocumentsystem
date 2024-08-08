from celery_app import celery_app
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.user.user_service import UserService
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from app.services.sync.sync_service import SyncService

@celery_app.task
def sync_drive_to_pinecone(user_id):
    user_service = UserService()
    user = user_service.get_user(user_id)
    
    if not user:
        return {"error": f"User with id {user_id} not found"}

    credentials = Credentials.from_authorized_user_info(user['credentials'])
    sync_service = DrivePineconeSync(user_id, credentials)
    
    last_sync_time = user.get('last_sync_time')
    if last_sync_time:
        sync_service.incremental_sync(last_sync_time)
    else:
        sync_service.full_sync()
    
    # Update last sync time
    new_last_sync_time = datetime.now(timezone.utc).isoformat()
    user_service.update_last_sync_time(user_id, new_last_sync_time)

    return {"message": f"Sync completed for user {user_id}"}

# Remove the setup_periodic_tasks function as it's no longer needed