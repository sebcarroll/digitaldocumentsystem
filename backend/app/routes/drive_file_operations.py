from flask import Blueprint, request, jsonify, session
from app.services.google_drive.file_operations import DriveFileOperations

drive_file_ops_bp = Blueprint('drive_file_ops', __name__)

@drive_file_ops_bp.route('/drive/<file_id>/open', methods=['GET'])
def open_file(file_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.open_file(file_id)

@drive_file_ops_bp.route('/drive/upload-file', methods=['POST'])
def upload_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    file = request.files['file']
    folder_id = request.form.get('folderId', 'root')
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.upload_file(file, folder_id)

@drive_file_ops_bp.route('/drive/create-doc', methods=['POST'])
def create_doc():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    folder_id = data.get('folderId', 'root')
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.create_doc(folder_id)

@drive_file_ops_bp.route('/drive/create-sheet', methods=['POST'])
def create_sheet():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    folder_id = data.get('folderId', 'root')
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.create_sheet(folder_id)

@drive_file_ops_bp.route('/drive/move-files', methods=['POST'])
def move_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.move_files(data['fileIds'], data['newFolderId'])

@drive_file_ops_bp.route('/drive/delete-files', methods=['POST'])
def delete_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.delete_files(data['fileIds'])

@drive_file_ops_bp.route('/drive/copy-files', methods=['POST'])
def copy_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.copy_files(data['fileIds'])

@drive_file_ops_bp.route('/drive/rename-file', methods=['POST'])
def rename_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    drive_ops = DriveFileOperations(session['credentials'])
    return drive_ops.rename_file(data['fileId'], data['newName'])