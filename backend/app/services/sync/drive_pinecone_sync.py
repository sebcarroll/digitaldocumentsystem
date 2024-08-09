from app.services.google_drive.google_drive_service import GoogleDriveService
from app.services.database.pinecone_manager import PineconeManager
from database.schemas.document import DocumentSchema
from database.schemas.folder import FolderSchema
from database.schemas.sync_log import SyncLogSchema
from database.schemas.embedding_job import EmbeddingJobSchema
import logging
from datetime import datetime
import uuid
from config import Config
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

class DrivePineconeSync:
    def __init__(self, user_id, drive_service):
        self.user_id = user_id
        self.drive_service = drive_service
        self.pinecone_manager = PineconeManager(
            api_key=Config.PINECONE_API_KEY,
            environment=Config.PINECONE_ENVIRONMENT,
            index_name=Config.PINECONE_INDEX_NAME,
            openai_api_key=Config.OPENAI_API_KEY
        )
        self.document_schema = DocumentSchema()
        self.folder_schema = FolderSchema()
        self.sync_log_schema = SyncLogSchema()
        self.embedding_job_schema = EmbeddingJobSchema()

    def sync_file(self, file_id):
        try:
            file_metadata = self.drive_service.get_file_metadata(file_id)
            file_content = self.drive_service.get_file_content(file_id)

            document = {
                'id': str(uuid.uuid4()),
                'googleDriveId': file_id,
                'title': file_metadata['name'],
                'mimeType': file_metadata['mimeType'],
                'createdAt': file_metadata['createdTime'],
                'modifiedAt': file_metadata['modifiedTime'],
                'ownerId': file_metadata['owners'][0]['emailAddress'],
                'parentFolderId': file_metadata.get('parents', [None])[0],
                'webViewLink': file_metadata.get('webViewLink'),
                'lastSyncTime': datetime.now(datetime.UTC).isoformat(),
                'version': 1,
                'accessControl': {
                    'ownerId': file_metadata['owners'][0]['emailAddress'],
                    'readers': [user['emailAddress'] for user in file_metadata.get('permissions', []) if user.get('role') == 'reader'],
                    'writers': [user['emailAddress'] for user in file_metadata.get('permissions', []) if user.get('role') == 'writer']
                },
                'content': file_content
            }

            validated_document = self.document_schema.load(document)
            self.pinecone_manager.upsert_document(validated_document)

            logger.info(f"Synced file {file_id} to Pinecone")
        except Exception as e:
            logger.error(f"Error syncing file {file_id}: {str(e)}")

    def sync_folder(self, folder_id='root'):
        try:
            folder_metadata = self.drive_service.get_folder_metadata(folder_id)
            
            folder = {
                'id': str(uuid.uuid4()),
                'googleDriveId': folder_id,
                'name': folder_metadata['name'],
                'parentFolderId': folder_metadata.get('parents', [None])[0],
                'createdAt': folder_metadata['createdTime'],
                'modifiedAt': folder_metadata['modifiedTime'],
                'ownerId': folder_metadata['owners'][0]['emailAddress'],
                'lastSyncTime': datetime.now(datetime.UTC).isoformat(),
                'accessControl': {
                    'ownerId': folder_metadata['owners'][0]['emailAddress'],
                    'readers': [user['emailAddress'] for user in folder_metadata.get('permissions', []) if user.get('role') == 'reader'],
                    'writers': [user['emailAddress'] for user in folder_metadata.get('permissions', []) if user.get('role') == 'writer']
                }
            }

            validated_folder = self.folder_schema.load(folder)
            # Store folder metadata if needed

            files = self.drive_service.list_folder_contents(folder_id)
            for file in files:
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    self.sync_folder(file['id'])
                else:
                    self.sync_file(file['id'])
        except Exception as e:
            logger.error(f"Error syncing folder {folder_id}: {str(e)}")

    def full_sync(self):
        sync_log = {
            'id': str(uuid.uuid4()),
            'userId': self.user_id,
            'startTime': datetime.now(datetime.UTC).isoformat(),
            'status': 'in_progress',
            'syncType': 'full'
        }
        
        try:
            self.sync_folder()
            sync_log['status'] = 'completed'
        except Exception as e:
            sync_log['status'] = 'failed'
            sync_log['errors'] = [str(e)]
        finally:
            sync_log['endTime'] = datetime.now(datetime.UTC).isoformat()
            validated_sync_log = self.sync_log_schema.load(sync_log)
            self.store_sync_log(validated_sync_log)

    def incremental_sync(self, last_sync_time):
        sync_log = {
            'id': str(uuid.uuid4()),
            'userId': self.user_id,
            'startTime': datetime.now(datetime.UTC).isoformat(),
            'status': 'in_progress',
            'syncType': 'incremental'
        }
        
        try:
            changed_files = self.drive_service.list_changed_files(last_sync_time)
            for file in changed_files:
                self.sync_file(file['id'])
            sync_log['status'] = 'completed'
            sync_log['changesProcessed'] = len(changed_files)
        except Exception as e:
            sync_log['status'] = 'failed'
            sync_log['errors'] = [str(e)]
        finally:
            sync_log['endTime'] = datetime.now(datetime.UTC).isoformat()
            validated_sync_log = self.sync_log_schema.load(sync_log)
            self.store_sync_log(validated_sync_log)

    def store_sync_log(self, sync_log):
        # Implement method to store sync log
        # This could be stored in a separate database or logging system
        pass

    def handle_file_open(self, file_id):
        self.sync_file(file_id)

    def handle_file_close(self, file_id):
        self.sync_file(file_id)

    def handle_file_change(self, file_id):
        self.sync_file(file_id)