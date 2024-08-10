import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    SCOPES = [
        'https://www.googleapis.com/auth/contacts.readonly',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid',
        'https://www.googleapis.com/auth/userinfo.email'
    ]
    DEBUG = False

    # Redis configuration for storing tokens
    REDIS_TOKEN_URL = os.getenv('REDIS_TOKEN_URL')

    # Pinecone configuration
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Celery configuration
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')

    @classmethod
    def init_app(cls, app):
        app.config.update(
            broker_url=cls.broker_url,
            result_backend=cls.result_backend
        )

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

class TestingConfig(Config):
    TESTING = True
    
    # Use the real Pinecone API key and environment for testing
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
    
    # For OpenAI, you might still want to use a test key or mock it
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Use in-memory broker for Celery in testing
    broker_url = 'memory://'
    result_backend = 'memory://'