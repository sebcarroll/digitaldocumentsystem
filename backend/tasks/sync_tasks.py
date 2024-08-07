from backend.celery_app import celery
from backend.app.services.sync.drive_pinecone_sync import DrivePineconeSync
from backend.app.services.user.user_service import UserService
from datetime import datetime

@celery.task
def sync_drive_to_pinecone(user_id):
    user_service = UserService()
    user = user_service.get_user(user_id)
    
    sync_service = DrivePineconeSync(user_id, user['credentials'])
    
    last_sync_time = user.get('lastSyncTime')
    if last_sync_time:
        sync_service.incremental_sync(last_sync_time)
    else:
        sync_service.full_sync()
    
    # Update last sync time
    new_last_sync_time = datetime.utcnow().isoformat()
    user_service.update_last_sync_time(user_id, new_last_sync_time)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls sync_drive_to_pinecone every hour
    sender.add_periodic_task(3600.0, sync_drive_to_pinecone.s(), name='sync every hour')