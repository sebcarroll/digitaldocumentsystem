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
chat_service = None

@chat_bp.before_request
def initialize_chat_service():
    global chat_service
    if chat_service is None:
        chat_service = ChatService()

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
        result = chat_service.query(query)
        logger.info(f"Query processed successfully, result: {result}")
        return jsonify({"response": result})
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the query"}), 500

@chat_bp.route('/clear', methods=['POST'])
def clear_chat_history():
    global chat_service
    if chat_service:
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
    try:
        if not chat_service.has_drive_core():
            try:
                drive_core = get_drive_core(session)
                chat_service.set_drive_core(drive_core)
            except ValueError as e:
                return jsonify({"error": "Google credentials required for document management"}), 401

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