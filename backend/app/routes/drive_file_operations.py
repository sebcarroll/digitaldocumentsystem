from flask import Blueprint, request, jsonify, session
from app.services.google_drive.file_operations import DriveFileOperations
from app.utils.drive_utils import get_drive_core

drive_file_ops_bp = Blueprint('drive_file_ops', __name__)

@drive_file_ops_bp.route('/drive/<file_id>/open', methods=['GET'])
def open_file(file_id):
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        return jsonify(drive_ops.open_file(file_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/upload-file', methods=['POST'])
def upload_file():
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        file = request.files['file']
        folder_id = request.form.get('folderId', 'root')
        return jsonify(drive_ops.upload_file(file, folder_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/create-doc', methods=['POST'])
def create_doc():
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        folder_id = data.get('folderId', 'root')
        return jsonify(drive_ops.create_doc(folder_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/create-sheet', methods=['POST'])
def create_sheet():
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        folder_id = data.get('folderId', 'root')
        return jsonify(drive_ops.create_sheet(folder_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/move-files', methods=['POST'])
def move_files():
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.move_files(data['fileIds'], data['newFolderId']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/delete-files', methods=['POST'])
def delete_files():
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.delete_files(data['fileIds']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/copy-files', methods=['POST'])
def copy_files():
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.copy_files(data['fileIds']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/rename-file', methods=['POST'])
def rename_file():
    try:
        drive_core = get_drive_core(session)
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.rename_file(data['fileId'], data['newName']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500