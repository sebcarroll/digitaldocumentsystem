"""
Chat routes module for the Google Drive Sync API.

This module defines the routes for chat functionality, including
query processing and document management in the vector store.
"""

from flask import Blueprint, request, jsonify
from app.services.natural_language.chat_service import ChatService
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()

@chat_bp.route('/query', methods=['POST'])
def query_llm():
    """
    Process a query and return a response from the language model.

    Returns:
        dict: A JSON response containing the query result or an error message.
    """
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

@chat_bp.route('/document', methods=['POST', 'PUT', 'DELETE'])
def manage_document():
    """
    Manage documents in the vector store.

    This endpoint handles creation, updating, and deletion of documents.

    Returns:
        dict: A JSON response indicating the result of the operation.
    """
    try:
        if request.method in ['POST', 'PUT']:
            data = request.json
            logger.debug(f"Received document data: {data}")
            document = data.get('document')
            
            if not document:
                logger.warning("No document provided")
                return jsonify({"error": "No document provided"}), 400

            logger.info(f"Processing document: {document}")
            success = chat_service.add_document(document)
            
            if success:
                logger.info("Document processed and stored successfully")
                return jsonify({"message": "Document processed and stored successfully"})
            else:
                logger.error("Failed to process document")
                return jsonify({"error": "Failed to process document"}), 500

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