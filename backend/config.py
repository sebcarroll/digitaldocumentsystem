"""Configuration module for the application.

This module defines configuration classes for different environments
(development, production, testing) and loads environment variables.
"""

import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    """Base configuration class."""

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

    # Session configuration
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'diganise_session:'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

class DevelopmentConfig(Config):
    """Configuration for development environment."""

    DEBUG = True

class ProductionConfig(Config):
    """Configuration for production environment."""

    # You might want to adjust session lifetime for production
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)

class TestingConfig(Config):
    """Configuration for testing environment."""

    TESTING = True
    
    # Use the real Pinecone API key and environment for testing
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
    
    # For OpenAI, you might still want to use a test key or mock it
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    