from flask import Blueprint, request, jsonify, session
from app.services.google_drive.folder_operations import DriveFolderOperations

drive_folder_ops_bp = Blueprint('drive_folder_ops', __name__)

@drive_folder_ops_bp.route('/drive/create-folder', methods=['POST'])
def create_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    parent_folder_id = data.get('parentFolderId', 'root')
    folder_name = data.get('folderName')
    folder_ops = DriveFolderOperations(session['credentials'])
    return folder_ops.create_folder(parent_folder_id, folder_name)

@drive_folder_ops_bp.route('/drive/upload-folder', methods=['POST'])
def upload_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    parent_folder_id = request.form.get('parentFolderId', 'root')
    files = request.files.getlist('files')
    folder_ops = DriveFolderOperations(session['credentials'])
    return folder_ops.upload_folder(parent_folder_id, files)

@drive_folder_ops_bp.route('/drive/folders', methods=['GET'])
def fetch_folders():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    parent_id = request.args.get('parent_id', 'root')
    folder_ops = DriveFolderOperations(session['credentials'])
    return folder_ops.fetch_folders(parent_id)