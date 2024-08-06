from flask import Blueprint, request, jsonify, session
from .drive_core import get_services
from googleapiclient.http import MediaIoBaseUpload
import io
import os

drive_folder_ops_bp = Blueprint('drive_folder_ops', __name__)

@drive_folder_ops_bp.route('/drive/create-folder', methods=['POST'])
def create_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    parent_folder_id = data.get('parentFolderId', 'root')
    folder_name = data.get('folderName')

    drive_service, _ = get_services()
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    return jsonify({"id": file.get('id')})


@drive_folder_ops_bp.route('/drive/upload-folder', methods=['POST'])
def upload_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    parent_folder_id = request.form.get('parentFolderId', 'root')
    files = request.files.getlist('files')

    drive_service, _ = get_services()
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

@drive_folder_ops_bp.route('/drive/folders', methods=['GET'])
def fetch_folders():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    parent_id = request.args.get('parent_id', 'root')
    
    try:
        results = drive_service.files().list(
            q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name)',
            supportsAllDrives=True
        ).execute()
        
        folders = results.get('files', [])
        return jsonify({"folders": folders})
    except Exception as e:
        return jsonify({"error": str(e)}), 400