"""
This module provides Flask routes for synchronization operations between Google Drive and Pinecone.

It includes functionality for starting and ending sync sessions, and handling file events.
"""

from flask import Blueprint, jsonify, request, session
from tasks.sync_tasks import sync_drive_to_pinecone
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from app.services.user.user_service import UserService
from google.oauth2.credentials import Credentials

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync/start_session', methods=['POST'])
def start_sync_session():
    """
    Start a synchronization session between Google Drive and Pinecone.

    This function initiates an asynchronous task to sync the user's Google Drive with Pinecone.

    Returns:
        flask.Response: A JSON response indicating the start of the sync session.

    Raises:
        401: If the user is not authenticated.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    sync_drive_to_pinecone.delay(user_id)
    return jsonify({"message": "Sync session started"}), 200

@sync_bp.route('/sync/end_session', methods=['POST'])
def end_sync_session():
    """
    End a synchronization session between Google Drive and Pinecone.

    This function initiates an asynchronous task to finalize the sync process.

    Returns:
        flask.Response: A JSON response indicating the end of the sync session.

    Raises:
        401: If the user is not authenticated.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    sync_drive_to_pinecone.delay(user_id)
    return jsonify({"message": "Sync session ended"}), 200

@sync_bp.route('/sync/file_event', methods=['POST'])
def handle_file_event():
    """
    Handle file events for synchronization between Google Drive and Pinecone.

    This function processes file events (open, close, change) and updates the sync state accordingly.

    Returns:
        flask.Response: A JSON response indicating the file event was processed.

    Raises:
        401: If the user is not authenticated.
        400: If the event_type or file_id is missing, or if the event_type is invalid.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    event_type = request.json.get('event_type')
    file_id = request.json.get('file_id')
    
    if not event_type or not file_id:
        return jsonify({"error": "Missing event_type or file_id"}), 400
    
    user_service = UserService()
    user = user_service.get_user(user_id)
    credentials = Credentials.from_authorized_user_info(user['credentials'])
    sync_service = DrivePineconeSync(user_id, credentials)
    
    if event_type == 'open':
        sync_service.handle_file_open(file_id)
    elif event_type == 'close':
        sync_service.handle_file_close(file_id)
    elif event_type == 'change':
        sync_service.handle_file_change(file_id)
    else:
        return jsonify({"error": "Invalid event_type"}), 400
    
    return jsonify({"message": "File event processed"}), 200