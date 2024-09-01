"""
Chat routes module for the Google Drive Sync API.

This module defines the routes for chat functionality, including
query processing and document management in the vector store.
"""

from flask import Blueprint, request, jsonify, session, current_app, make_response
from app.services.natural_language.chat_service import ChatService
import logging
from app.utils.drive_utils import get_drive_core

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

@chat_bp.before_request
def initialize_chat_service():
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
            # Log the error but don't raise an exception
            logger.warning("Failed to initialize drive_core for chat service")

@chat_bp.route('/query', methods=['POST'])
def query_llm():
    logger.info("Received chat query request")
    try:
        data = request.json
        logger.debug(f"Received query data: {data}")
        query = data.get('query')
        
        if not query:
            logger.warning("No query provided")
            return jsonify({"error": "No query provided"}), 400

        logger.info(f"Processing query: {query}")
        chat_service = current_app.extensions['chat_service']
        result = chat_service.query(query)
        logger.info(f"Query processed successfully, result: {result}")
        return jsonify({"response": result})
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the query"}), 500

@chat_bp.route('/clear', methods=['POST'])
def clear_chat_history():
    chat_service = current_app.extensions['chat_service']
    chat_service.clear_memory()
    return jsonify({"message": "Chat history cleared"}), 200

@chat_bp.route('/document', methods=['POST', 'PUT', 'DELETE'])
def manage_document():
    """
    Manage documents in the vector store.

    This endpoint handles creation, updating, and deletion of documents.

    Returns:
        dict: A JSON response indicating the result of the operation.
    """
    chat_service = current_app.extensions['chat_service']
    try:
        if request.method in ['POST', 'PUT']:
            data = request.json
            logger.debug(f"Received document data: {data}")
            file_id = data.get('file_id')
            file_name = data.get('file_name')
            
            if not file_id or not file_name:
                logger.warning("File ID or name not provided")
                return jsonify({"error": "File ID and name are required"}), 400

            logger.info(f"Processing file: {file_name} with ID: {file_id}")
            success = chat_service.process_and_add_file(file_id, file_name)
            
            if success:
                logger.info("File processed and stored successfully")
                return jsonify({"message": "File processed and stored successfully"})
            else:
                logger.error("Failed to process file")
                return jsonify({"error": "Failed to process file"}), 500

        elif request.method == 'DELETE':
            data = request.json
            logger.debug(f"Received delete request data: {data}")
            document_id = data.get('document_id')
            
            if not document_id:
                logger.warning("No document ID provided")
                return jsonify({"error": "No document ID provided"}), 400

            logger.info(f"Deleting document with ID: {document_id}")
            success = chat_service.delete_document(document_id)
            
            if success:
                logger.info("Document deleted successfully")
                return jsonify({"message": "Document deleted successfully"})
            else:
                logger.error("Failed to delete document")
                return jsonify({"error": "Failed to delete document"}), 500
    except Exception as e:
        logger.error(f"Error in manage_document: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while managing the document"}), 500

@chat_bp.route('/update-document-selection', methods=['POST'])
def update_document_selection():
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
        logger.error(f"Error in update_document_selection: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while updating document selection"}), 500

@chat_bp.route('', defaults={'path': ''})
@chat_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    try:
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        logger.error(f"Error handling OPTIONS request: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while handling OPTIONS request"}), 500

@chat_bp.before_request
def log_request_info():
    logger.debug('Chat BP - Request Method: %s', request.method)
    logger.debug('Chat BP - Request URL: %s', request.url)
    logger.debug('Chat BP - Request Headers: %s', request.headers)

@chat_bp.route('/upload-documents', methods=['POST'])
def upload_documents():
    chat_service = current_app.extensions['chat_service']
    try:
        data = request.json
        file_ids = data.get('fileIds', [])
        file_names = data.get('fileNames', [])
        
        if not file_ids or not file_names or len(file_ids) != len(file_names):
            logger.warning("Invalid file data provided")
            return jsonify({"error": "Invalid file data provided"}), 400

        result = chat_service.process_and_add_multiple_files(file_ids, file_names)

        logger.info(f"Uploaded {result['successful_uploads']} out of {result['total_files']} documents")
        return jsonify({
            "message": f"Processed {result['successful_uploads']} out of {result['total_files']} documents successfully",
            "successful_uploads": result['successful_uploads'],
            "total_files": result['total_files']
        })
    except Exception as e:
        logger.error(f"Error in upload_documents: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while uploading documents"}), 500
    
@chat_bp.route('/set-documents-unselected', methods=['POST'])
def set_documents_unselected():
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
        logger.error(f"Error in set_documents_unselected: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while updating documents"}), 500