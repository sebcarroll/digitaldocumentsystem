from flask import current_app
from .pinecone_manager import PineconeManager

pinecone_manager = None

def init_db(app):
    global pinecone_manager
    pinecone_manager = PineconeManager(
        api_key=app.config['PINECONE_API_KEY'],
        index_name=app.config['PINECONE_INDEX_NAME'],
        openai_api_key=app.config['OPENAI_API_KEY']
    )

def get_db():
    if pinecone_manager is None:
        init_db(current_app)
    return pinecone_manager