"""
This module provides functionality for synchronizing Google Drive files with Pinecone.

It contains the DrivePineconeSync class which handles the synchronization process,
including file and folder syncing, full and incremental syncs, and error handling.
"""

from app.services.google_drive.google_drive_service import GoogleDriveService
from app.services.database.pinecone_manager_service import PineconeManager
from database.schemas.document import DocumentSchema
from database.schemas.folder import FolderSchema
from database.schemas.sync_log import SyncLogSchema
from database.schemas.embedding_job import EmbeddingJobSchema
import logging
from datetime import datetime, timezone
import uuid
from config import Config
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

class DrivePineconeSync:
    """
    A class to handle synchronization between Google Drive and Pinecone.

    This class provides methods for syncing individual files, folders,
    performing full and incremental syncs, and handling file events.
    """

    def __init__(self, user_id, drive_service):
        """
        Initialize the DrivePineconeSync instance.

        Args:
            user_id (str): The ID of the user.
            drive_service (GoogleDriveService): An instance of the Google Drive service.
        """
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
        """
        Synchronize a single file from Google Drive to Pinecone.

        Args:
            file_id (str): The ID of the file to synchronize.
        """
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
                'lastSyncTime': datetime.now(timezone.utc).isoformat(),
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

    def sync_folder(self, folder_id='root', depth=0, max_depth=10):
        """
        Synchronize a folder and its contents from Google Drive to Pinecone.

        Args:
            folder_id (str, optional): The ID of the folder to synchronize. Defaults to 'root'.
            depth (int): Current recursion depth.
            max_depth (int): Maximum allowed recursion depth.
        """
        if depth > max_depth:
            logger.warning(f"Maximum folder depth reached for folder {folder_id}")
            return

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
                'lastSyncTime': datetime.now(timezone.utc).isoformat(),
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
                    self.sync_folder(file['id'], depth=depth+1, max_depth=max_depth)
                else:
                    self.sync_file(file['id'])
        except Exception as e:
            logger.error(f"Error syncing folder {folder_id}: {str(e)}")
            
    def full_sync(self):
        """Perform a full synchronization of all files and folders."""
        sync_log = {
            'id': str(uuid.uuid4()),
            'userId': self.user_id,
            'startTime': datetime.now(timezone.utc).isoformat(),
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
            sync_log['endTime'] = datetime.now(timezone.utc).isoformat()
            validated_sync_log = self.sync_log_schema.load(sync_log)
            self.store_sync_log(validated_sync_log)

    def incremental_sync(self, last_sync_time):
        """
        Perform an incremental synchronization of files changed since the last sync.

        Args:
            last_sync_time (datetime): The timestamp of the last synchronization.
        """
        sync_log = {
            'id': str(uuid.uuid4()),
            'userId': self.user_id,
            'startTime': datetime.now(timezone.utc).isoformat(),
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
            sync_log['endTime'] = datetime.now(timezone.utc).isoformat()
            validated_sync_log = self.sync_log_schema.load(sync_log)
            self.store_sync_log(validated_sync_log)

    def store_sync_log(self, sync_log):
        """
        Store the synchronization log.

        Args:
            sync_log (dict): The synchronization log to store.
        """
        # Implement method to store sync log
        # This could be stored in a separate database or logging system
        pass

    def handle_file_open(self, file_id):
        """
        Handle a file open event.

        Args:
            file_id (str): The ID of the file that was opened.
        """
        self.sync_file(file_id)

    def handle_file_close(self, file_id):
        """
        Handle a file close event.

        Args:
            file_id (str): The ID of the file that was closed.
        """
        self.sync_file(file_id)

    def handle_file_change(self, file_id):
        """
        Handle a file change event.

        Args:
            file_id (str): The ID of the file that was changed.
        """
        self.sync_file(file_id)