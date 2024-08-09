from flask import Blueprint, session, jsonify
from app.utils.drive_utils import get_drive_core

drive_core_bp = Blueprint('drive_core', __name__)

@drive_core_bp.route('/drive/list_folder_contents/<folder_id>')
def list_folder_contents(folder_id):
    try:
        drive_core = get_drive_core(session)
        drive_service = drive_core.drive_service
        
        results = []
        page_token = None
        while True:
            response = drive_service.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token,
                supportsAllDrives=True
            ).execute()
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        
        return jsonify(results)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
