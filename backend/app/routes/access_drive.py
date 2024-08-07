from flask import Blueprint, redirect, session, url_for, jsonify, request, g
from app.services.google_drive.drive_service import DriveService

drive_bp = Blueprint('drive', __name__)

@drive_bp.route('/drive')
def drive():
    folder_id = request.args.get('folder_id', 'root')
    page_token = request.args.get('page_token')
    page_size = int(request.args.get('page_size', 100))

    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    drive_service = DriveService(session)
    
    try:
        file_list, next_page_token = drive_service.list_folder_contents(folder_id, page_token, page_size)
        
        if not file_list:
            return jsonify({"message": "No files found in this folder."})
        else:
            return jsonify({
                "files": file_list,
                "nextPageToken": next_page_token
            })

    except Exception as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500

@drive_bp.route('/drive/<file_id>/open')
def open_file(file_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service = DriveService(session)

    try:
        web_view_link, mime_type = drive_service.get_file_web_view_link(file_id)
        return jsonify({"webViewLink": web_view_link, "mimeType": mime_type})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_bp.teardown_app_request
def cleanup_services(exception=None):
    if 'credentials' in session:
        drive_service = DriveService(session)
        drive_service.cleanup_services()

@drive_bp.route('/logout')
def logout():
    cleanup_services()
    session.clear()
    return jsonify({"message": "Logged out successfully"})