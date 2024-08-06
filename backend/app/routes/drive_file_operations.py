from flask import Blueprint, request, jsonify, session
from .drive_core import get_services
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os


drive_file_ops_bp = Blueprint('drive_file_ops', __name__)

@drive_file_ops_bp.route('/drive/<file_id>/open', methods=['GET'])
def open_file(file_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    
    try:
        file = drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
        return jsonify({"webViewLink": file.get('webViewLink')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_file_ops_bp.route('/drive/upload-file', methods=['POST'])
def upload_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    file = request.files['file']
    folder_id = request.form.get('folderId', 'root')

    drive_service, _ = get_services()
    file_metadata = {'name': file.filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()),
                              mimetype=file.content_type,
                              resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return jsonify({"id": file.get('id')})

@drive_file_ops_bp.route('/drive/create-doc', methods=['POST'])
def create_doc():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    folder_id = data.get('folderId', 'root')

    drive_service, _ = get_services()
    file_metadata = {
        'name': 'Untitled document',
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    return jsonify({
        "id": file.get('id'),
        "webViewLink": file.get('webViewLink')
    })

@drive_file_ops_bp.route('/drive/create-sheet', methods=['POST'])
def create_sheet():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    folder_id = data.get('folderId', 'root')

    drive_service, _ = get_services()
    file_metadata = {
        'name': 'Untitled spreadsheet',
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    return jsonify({
        "id": file.get('id'),
        "webViewLink": file.get('webViewLink')
    })  

@drive_file_ops_bp.route('/drive/move-files', methods=['POST'])
def move_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_ids = data.get('fileIds', [])
    new_folder_id = data.get('newFolderId')

    drive_service, _ = get_services()
    
    moved_files = []
    errors = []

    for file_id in file_ids:
        try:
            file = drive_service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            file = drive_service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            moved_files.append({"id": file.get('id'), "parents": file.get('parents')})
        except Exception as e:
            errors.append(f"Failed to move file {file_id}: {str(e)}")

    if errors:
        return jsonify({"error": "; ".join(errors), "moved_files": moved_files}), 400
    
    return jsonify({"message": "Files moved successfully", "moved_files": moved_files})

@drive_file_ops_bp.route('/drive/delete-files', methods=['POST'])
def delete_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_ids = data.get('fileIds', [])

    drive_service, _ = get_services()
    
    deleted_files = []
    errors = []

    for file_id in file_ids:
        try:
            drive_service.files().delete(fileId=file_id).execute()
            deleted_files.append(file_id)
        except Exception as e:
            errors.append(f"Failed to delete file {file_id}: {str(e)}")

    if errors:
        return jsonify({"error": "; ".join(errors), "deleted_files": deleted_files}), 400
    
    return jsonify({"message": "Files deleted successfully", "deleted_files": deleted_files})

@drive_file_ops_bp.route('/drive/copy-files', methods=['POST'])
def copy_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_ids = data.get('fileIds', [])

    drive_service, _ = get_services()
    
    copied_files = []
    errors = []

    for file_id in file_ids:
        try:
            copied_file = drive_service.files().copy(fileId=file_id, fields='id, name').execute()
            copied_files.append({"id": copied_file.get('id'), "name": copied_file.get('name')})
        except Exception as e:
            errors.append(f"Failed to copy file {file_id}: {str(e)}")

    if errors:
        return jsonify({"error": "; ".join(errors), "copied_files": copied_files}), 400
    
    return jsonify({"message": "Files copied successfully", "copied_files": copied_files})

@drive_file_ops_bp.route('/drive/rename-file', methods=['POST'])
def rename_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_id = data.get('fileId')
    new_name = data.get('newName')

    drive_service, _ = get_services()
    
    try:
        file = drive_service.files().update(
            fileId=file_id,
            body={'name': new_name},
            fields='id, name'
        ).execute()
        return jsonify({"id": file.get('id'), "name": file.get('name')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400