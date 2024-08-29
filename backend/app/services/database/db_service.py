"""Database service module for managing Pinecone connections."""

from flask import current_app
from app.services.database.pinecone_manager_service import PineconeManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pinecone_manager = None

def init_db(app):
    """
    Initialize the Pinecone database connection.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        None

    Raises:
        Exception: If initialization of the Pinecone manager fails.
    """
    global pinecone_manager
    pinecone_manager = None  # Reset pinecone_manager at the start
    logger.info("Initializing Pinecone manager")
    logger.info(f"PINECONE_API_KEY: {'set' if app.config['PINECONE_API_KEY'] else 'not set'}")
    logger.info(f"PINECONE_ENVIRONMENT: {app.config['PINECONE_ENVIRONMENT']}")
    logger.info(f"PINECONE_INDEX_NAME: {app.config['PINECONE_INDEX_NAME']}")

    try:
        pinecone_manager = PineconeManager(
            api_key=app.config['PINECONE_API_KEY'],
            environment=app.config['PINECONE_ENVIRONMENT'],
            index_name=app.config['PINECONE_INDEX_NAME'],
        )
        logger.info("Pinecone manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone manager: {str(e)}")
        pinecone_manager = None  # Ensure it's None on exception
        raise

def get_db():
    """
    Get the Pinecone database connection.

    Returns:
        PineconeManager: The initialized Pinecone manager instance.

    Raises:
        RuntimeError: If the Pinecone manager initialization fails.
    """
    global pinecone_manager
    if pinecone_manager is None:
        logger.warning("Pinecone manager is None, initializing...")
        try:
            init_db(current_app)
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone manager: {str(e)}")
            raise RuntimeError("Pinecone manager initialization failed") from e
    if pinecone_manager is None:
        raise RuntimeError("Pinecone manager initialization failed")
    return pinecone_manager