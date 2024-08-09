from flask import Blueprint, request, jsonify, session
from app.services.google_drive.folder_operations import DriveFolderOperations
from app.utils.drive_utils import get_drive_core

drive_folder_ops_bp = Blueprint('drive_folder_ops', __name__)

@drive_folder_ops_bp.route('/drive/create-folder', methods=['POST'])
def create_folder():
    try:
        drive_core = get_drive_core(session)
        folder_ops = DriveFolderOperations(drive_core)
        data = request.json
        parent_folder_id = data.get('parentFolderId', 'root')
        folder_name = data.get('folderName')
        result = folder_ops.create_folder(parent_folder_id, folder_name)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_folder_ops_bp.route('/drive/upload-folder', methods=['POST'])
def upload_folder():
    try:
        drive_core = get_drive_core(session)
        folder_ops = DriveFolderOperations(drive_core)
        parent_folder_id = request.form.get('parentFolderId', 'root')
        files = request.files.getlist('files')
        result = folder_ops.upload_folder(parent_folder_id, files)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_folder_ops_bp.route('/drive/folders', methods=['GET'])
def fetch_folders():
    try:
        drive_core = get_drive_core(session)
        folder_ops = DriveFolderOperations(drive_core)
        parent_id = request.args.get('parent_id', 'root')
        result = folder_ops.fetch_folders(parent_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500