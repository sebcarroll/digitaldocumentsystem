"""
Chat routes module for the application.

This module defines the routes for chat functionality, including
query processing and document management in the vector store.
"""

from flask import Blueprint, request, jsonify, session, current_app, make_response
from app.services.natural_language.chat_service import ChatService
from app.utils.drive_utils import get_drive_core

chat_bp = Blueprint('chat', __name__)

@chat_bp.before_request
def initialize_chat_service():
    """
    Initialize the chat service before each request.

    This function sets up the chat service, associates it with the user,
    and initializes the drive core if necessary.
    """
    if 'chat_service' not in current_app.extensions:
        current_app.extensions['chat_service'] = ChatService()
    
    user_id = session.get('user_id')
    if user_id:
        current_app.extensions['chat_service'].set_user_id(user_id)
    
    if not current_app.extensions['chat_service'].has_drive_core():
        try:
            drive_core = get_drive_core(session)
            current_app.extensions['chat_service'].set_drive_core(drive_core)
        except ValueError:
            pass

@chat_bp.route('/query', methods=['POST'])
def query_llm():
    """
    Process a query using the language model.

    Returns:
        flask.Response: JSON response with the query result or error message.
    """
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400

        chat_service = current_app.extensions['chat_service']
        result = chat_service.query(query)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": "An error occurred while processing the query"}), 500

@chat_bp.route('/clear', methods=['POST'])
def clear_chat_history():
    """
    Clear the chat history.

    Returns:
        flask.Response: JSON response confirming the chat history was cleared.
    """
    chat_service = current_app.extensions['chat_service']
    chat_service.clear_memory()
    return jsonify({"message": "Chat history cleared"}), 200

@chat_bp.route('/document', methods=['POST', 'PUT', 'DELETE'])
def manage_document():
    """
    Manage documents in the vector store.

    This endpoint handles creation, updating, and deletion of documents.

    Returns:
        flask.Response: JSON response indicating the result of the operation.
    """
    chat_service = current_app.extensions['chat_service']
    try:
        if request.method in ['POST', 'PUT']:
            data = request.json
            file_id = data.get('file_id')
            file_name = data.get('file_name')
            
            if not file_id or not file_name:
                return jsonify({"error": "File ID and name are required"}), 400

            success = chat_service.process_and_add_file(file_id, file_name)
            
            if success:
                return jsonify({"message": "File processed and stored successfully"})
            else:
                return jsonify({"error": "Failed to process file"}), 500

        elif request.method == 'DELETE':
            data = request.json
            document_id = data.get('document_id')
            
            if not document_id:
                return jsonify({"error": "No document ID provided"}), 400

            success = chat_service.delete_document(document_id)
            
            if success:
                return jsonify({"message": "Document deleted successfully"})
            else:
                return jsonify({"error": "Failed to delete document"}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred while managing the document"}), 500

@chat_bp.route('/update-document-selection', methods=['POST'])
def update_document_selection():
    """
    Update the selection status of a document.

    Returns:
        flask.Response: JSON response indicating the result of the update.
    """
    chat_service = current_app.extensions['chat_service']
    try:
        data = request.json
        file_id = data.get('fileId')
        is_selected = data.get('isSelected')
        
        if file_id is None or is_selected is None:
            return jsonify({"error": "fileId and isSelected are required"}), 400

        result = chat_service.update_document_selection(file_id, is_selected)
        
        if result:
            return jsonify({"message": "Document selection updated successfully"})
        else:
            return jsonify({"error": "Failed to update document selection"}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred while updating document selection"}), 500

@chat_bp.route('', defaults={'path': ''})
@chat_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """
    Handle OPTIONS requests for CORS.

    Returns:
        flask.Response: Response with appropriate CORS headers.
    """
    try:
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        return jsonify({"error": "An error occurred while handling OPTIONS request"}), 500

@chat_bp.route('/upload-documents', methods=['POST'])
def upload_documents():
    """
    Upload and process multiple documents.

    Returns:
        flask.Response: JSON response with the upload results.
    """
    chat_service = current_app.extensions['chat_service']
    try:
        data = request.json
        file_ids = data.get('fileIds', [])
        file_names = data.get('fileNames', [])
        
        if not file_ids or not file_names or len(file_ids) != len(file_names):
            return jsonify({"error": "Invalid file data provided"}), 400

        result = chat_service.process_and_add_multiple_files(file_ids, file_names)

        return jsonify({
            "message": f"Processed {result['successful_uploads']} out of {result['total_files']} documents successfully",
            "successful_uploads": result['successful_uploads'],
            "total_files": result['total_files']
        })
    except Exception as e:
        return jsonify({"error": "An error occurred while uploading documents"}), 500
    
@chat_bp.route('/set-documents-unselected', methods=['POST'])
def set_documents_unselected():
    """
    Set multiple documents as unselected.

    Returns:
        flask.Response: JSON response with the update results.
    """
    chat_service = current_app.extensions['chat_service']
    try:
        data = request.json
        document_ids = data.get('documentIds', [])
        
        if not document_ids:
            return jsonify({"error": "No document IDs provided"}), 400

        results = []
        for doc_id in document_ids:
            success = chat_service.update_document_selection(doc_id, False)
            results.append({"id": doc_id, "success": success})

        return jsonify({
            "message": "Documents updated successfully",
            "results": results
        })
    except Exception as e:
        return jsonify({"error": "An error occurred while updating documents"}), 500