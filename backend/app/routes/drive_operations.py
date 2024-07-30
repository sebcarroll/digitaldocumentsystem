from flask import Blueprint, request, jsonify, session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os

drive_ops_bp = Blueprint('drive_ops', __name__)

def get_drive_service():
    credentials = Credentials(**session['credentials'])
    return build('drive', 'v3', credentials=credentials)

@drive_ops_bp.route('/drive/create-folder', methods=['POST'])
def create_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    parent_folder_id = data.get('parentFolderId', 'root')
    folder_name = data.get('folderName')

    drive_service = get_drive_service()
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    return jsonify({"id": file.get('id')})

@drive_ops_bp.route('/drive/upload-file', methods=['POST'])
def upload_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    file = request.files['file']
    folder_id = request.form.get('folderId', 'root')

    drive_service = get_drive_service()
    file_metadata = {'name': file.filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()),
                              mimetype=file.content_type,
                              resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return jsonify({"id": file.get('id')})

@drive_ops_bp.route('/drive/upload-folder', methods=['POST'])
def upload_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    parent_folder_id = request.form.get('parentFolderId', 'root')
    files = request.files.getlist('files')

    drive_service = get_drive_service()
    uploaded_files = []

    def create_folder(name, parent_id):
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')

    def upload_file(file, parent_id):
        file_metadata = {'name': os.path.basename(file.filename), 'parents': [parent_id]}
        media = MediaIoBaseUpload(io.BytesIO(file.read()),
                                  mimetype=file.content_type,
                                  resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    folder_structure = {}

    for file in files:
        path_parts = file.filename.split(os.path.sep)
        current_parent = parent_folder_id

        for i, part in enumerate(path_parts[:-1]):
            if i == 0:
                if part not in folder_structure:
                    folder_id = create_folder(part, current_parent)
                    folder_structure[part] = folder_id
                current_parent = folder_structure[part]
            else:
                parent_path = os.path.sep.join(path_parts[:i])
                current_path = os.path.sep.join(path_parts[:i+1])
                if current_path not in folder_structure:
                    folder_id = create_folder(part, current_parent)
                    folder_structure[current_path] = folder_id
                current_parent = folder_structure[current_path]

        file_id = upload_file(file, current_parent)
        uploaded_files.append({"name": file.filename, "id": file_id})

    return jsonify({"uploaded_files": uploaded_files})

@drive_ops_bp.route('/drive/create-doc', methods=['POST'])
def create_doc():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    folder_id = data.get('folderId', 'root')

    drive_service = get_drive_service()
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

@drive_ops_bp.route('/drive/create-sheet', methods=['POST'])
def create_sheet():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    folder_id = data.get('folderId', 'root')

    drive_service = get_drive_service()
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

@drive_ops_bp.route('/drive/move-file', methods=['POST'])
def move_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_id = data.get('fileId')
    new_folder_id = data.get('newFolderId')

    drive_service = get_drive_service()
    
    try:
        file = drive_service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        file = drive_service.files().update(
            fileId=file_id,
            addParents=new_folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        return jsonify({"id": file.get('id'), "parents": file.get('parents')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_ops_bp.route('/drive/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service = get_drive_service()
    
    try:
        drive_service.files().delete(fileId=file_id).execute()
        return jsonify({"message": "File deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_ops_bp.route('/drive/rename-file', methods=['POST'])
def rename_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_id = data.get('fileId')
    new_name = data.get('newName')

    drive_service = get_drive_service()
    
    try:
        file = drive_service.files().update(
            fileId=file_id,
            body={'name': new_name},
            fields='id, name'
        ).execute()
        return jsonify({"id": file.get('id'), "name": file.get('name')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_ops_bp.route('/drive/copy-file', methods=['POST'])
def copy_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_id = data.get('fileId')

    drive_service = get_drive_service()
    
    try:
        copied_file = drive_service.files().copy(fileId=file_id, fields='id, name').execute()
        return jsonify({"id": copied_file.get('id'), "name": copied_file.get('name')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400