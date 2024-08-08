from flask import current_app
from .pinecone_manager import PineconeManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pinecone_manager = None

def init_db(app):
    global pinecone_manager
    logger.info("Initializing Pinecone manager")
    logger.info(f"PINECONE_API_KEY: {'set' if app.config['PINECONE_API_KEY'] else 'not set'}")
    logger.info(f"PINECONE_ENVIRONMENT: {app.config['PINECONE_ENVIRONMENT']}")
    logger.info(f"PINECONE_INDEX_NAME: {app.config['PINECONE_INDEX_NAME']}")
    logger.info(f"OPENAI_API_KEY: {'set' if app.config['OPENAI_API_KEY'] else 'not set'}")

    try:
        pinecone_manager = PineconeManager(
            api_key=app.config['PINECONE_API_KEY'],
            environment=app.config['PINECONE_ENVIRONMENT'],
            index_name=app.config['PINECONE_INDEX_NAME'],
            openai_api_key=app.config['OPENAI_API_KEY']
        )
        logger.info("Pinecone manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone manager: {str(e)}")
        pinecone_manager = None

def get_db():
    global pinecone_manager
    if pinecone_manager is None:
        logger.warning("Pinecone manager is None, initializing...")
        init_db(current_app)
    if pinecone_manager is None:
        logger.error("Failed to initialize Pinecone manager")
        raise RuntimeError("Pinecone manager initialization failed")
    return pinecone_manager