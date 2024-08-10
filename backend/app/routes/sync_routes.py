from flask import Blueprint, jsonify, request, session
from tasks.sync_tasks import sync_drive_to_pinecone
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.user.user_service import UserService
from google.oauth2.credentials import Credentials
import logging

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync/start_session', methods=['POST'])
def start_sync_session():
    """
    Start a synchronization session between Google Drive and Pinecone.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        sync_drive_to_pinecone.delay(user_id)
        return jsonify({"message": "Sync session started"}), 200
    except Exception as e:
        logging.error(f"Error starting sync session: {str(e)}")
        return jsonify({"error": "Failed to start sync session"}), 500

@sync_bp.route('/sync/end_session', methods=['POST'])
def end_sync_session():
    """
    End a synchronization session between Google Drive and Pinecone.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        sync_drive_to_pinecone.delay(user_id)
        return jsonify({"message": "Sync session ended"}), 200
    except Exception as e:
        logging.error(f"Error ending sync session: {str(e)}")
        return jsonify({"error": "Failed to end sync session"}), 500

@sync_bp.route('/sync/file_event', methods=['POST'])
def handle_file_event():
    """
    Handle file events for synchronization between Google Drive and Pinecone.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    event_type = request.json.get('event_type')
    file_id = request.json.get('file_id')
    
    if not event_type or not file_id:
        return jsonify({"error": "Missing event_type or file_id"}), 400
    
    valid_event_types = ['open', 'close', 'change']
    if event_type not in valid_event_types:
        return jsonify({"error": "Invalid event_type"}), 400
    
    try:
        user_service = UserService()
        user = user_service.get_user(user_id)
        
        if not all(k in user['credentials'] for k in ('refresh_token', 'client_id', 'client_secret')):
            return jsonify({"error": "Invalid or incomplete credentials"}), 400
        
        credentials = Credentials.from_authorized_user_info(user['credentials'])
        sync_service = DrivePineconeSync(user_id, credentials)
        
        if event_type == 'open':
            sync_service.handle_file_open(file_id)
        elif event_type == 'close':
            sync_service.handle_file_close(file_id)
        elif event_type == 'change':
            sync_service.handle_file_change(file_id)
        
        return jsonify({"message": "File event processed"}), 200
    except Exception as e:
        logging.error(f"Error processing file event: {str(e)}")
        return jsonify({"error": "Failed to process file event"}), 500
