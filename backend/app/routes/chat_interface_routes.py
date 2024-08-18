"""
Chat routes module for the Google Drive Sync API.

This module defines the routes for chat functionality, including
query processing and document management in the vector store.
"""

from flask import Blueprint, request, jsonify, current_app, session
from app.services.natural_language.chat_service import ChatService
from app.utils.drive_utils import get_drive_core
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

def get_or_create_chat_service():
    """
    Get or create a ChatService instance.
    
    This function retrieves the ChatService instance from the application
    context if it exists, or creates a new one if it doesn't.
    
    Returns:
        ChatService: An instance of ChatService.
    """
    if 'chat_service' not in current_app.extensions:
        drive_core = get_drive_core()
        current_app.extensions['chat_service'] = ChatService(drive_core=drive_core)
    return current_app.extensions['chat_service']

@chat_bp.route('/query', methods=['POST'])
def query_llm():
    """
    Process a query and return a response from the language model.

    This function receives a query, processes it using the ChatService,
    and returns the response.

    Returns:
        dict: A JSON response containing the query result or an error message.
    """
    chat_service = get_or_create_chat_service()

    try:
        data = request.json
        logger.debug(f"Received query data: {data}")
        query = data.get('query')
        
        if not query:
            logger.warning("No query provided")
            return jsonify({"error": "No query provided"}), 400

        # Get the session_id from the current session
        session_id = session.get('session_id')
        if not session_id:
            logger.warning("No session_id found")
            return jsonify({"error": "No session_id found"}), 400

        logger.info(f"Processing query: {query} for session: {session_id}")
        result = chat_service.query(query, session_id)
        logger.info(f"Query processed successfully, result: {result}")
        return jsonify({"response": result})
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the query"}), 500

@chat_bp.route('/process_drive_file', methods=['POST'])
def process_drive_file():
    """
    Process and add a file from Google Drive.

    This endpoint requires Google Drive authentication. It processes
    a file from Google Drive and adds it to the vector store.

    Returns:
        dict: A JSON response indicating the result of the operation.
    """
    chat_service = get_or_create_chat_service()

    try:
        session_id = session.get('session_id')
        if not session_id:
            logger.warning("No session_id found")
            return jsonify({"error": "No session_id found"}), 400

        data = request.json
        file_id = data.get('file_id')
        file_name = data.get('file_name')

        if not file_id or not file_name:
            return jsonify({"error": "File ID and name are required"}), 400

        success = chat_service.process_and_add_file(file_id, file_name, session_id)
        if success:
            return jsonify({"message": "File processed and added successfully"})
        else:
            return jsonify({"error": "Failed to process and add file"}), 500
    except ValueError as ve:
        logger.error(f"ValueError in process_drive_file: {str(ve)}", exc_info=True)
        return jsonify({"error": str(ve)}), 403
    except Exception as e:
        logger.error(f"Error processing Drive file: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the Drive file"}), 500

@chat_bp.route('/delete_document', methods=['DELETE'])
def delete_document():
    """
    Delete a document from the vector store.

    This endpoint handles deletion of documents in the vector store.

    Returns:
        dict: A JSON response indicating the result of the operation.
    """
    chat_service = get_or_create_chat_service()

    try:
        session_id = session.get('session_id')
        if not session_id:
            logger.warning("No session_id found")
            return jsonify({"error": "No session_id found"}), 400

        data = request.json
        logger.debug(f"Received delete request data: {data}")
        document_id = data.get('document_id')
        
        if not document_id:
            logger.warning("No document ID provided")
            return jsonify({"error": "No document ID provided"}), 400

        logger.info(f"Deleting document with ID: {document_id} for session: {session_id}")
        success = chat_service.delete_document(document_id, session_id)
        
        if success:
            logger.info("Document deleted successfully")
            return jsonify({"message": "Document deleted successfully"})
        else:
            logger.error("Failed to delete document")
            return jsonify({"error": "Failed to delete document"}), 500
    except Exception as e:
        logger.error(f"Error in delete_document: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while deleting the document"}), 500

@chat_bp.route('/clear_session', methods=['POST'])
def clear_session():
    """
    Clear all vectors associated with the current session.

    This endpoint clears all vectors for the current session from the vector store.

    Returns:
        dict: A JSON response indicating the result of the operation.
    """
    chat_service = get_or_create_chat_service()

    try:
        session_id = session.get('session_id')
        if not session_id:
            logger.warning("No session_id found")
            return jsonify({"error": "No session_id found"}), 400

        logger.info(f"Clearing session: {session_id}")
        result = chat_service.clear_session(session_id)
        
        if result['success']:
            logger.info(f"Session cleared successfully. Vectors deleted: {result['vectors_deleted']}")
            return jsonify({"message": f"Session cleared successfully. Vectors deleted: {result['vectors_deleted']}"})
        else:
            logger.error("Failed to clear session")
            return jsonify({"error": "Failed to clear session"}), 500
    except Exception as e:
        logger.error(f"Error in clear_session: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while clearing the session"}), 500