import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Secret key for Flask sessions
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Google OAuth credentials
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    # Google API scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
    # Database URL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    # Debug mode off by default
    DEBUG = False

class DevelopmentConfig(Config):
    # Enable debug mode for development
    DEBUG = True

class ProductionConfig(Config):
    # Production-specific settings can be added here
    pass

class TestingConfig(Config):
    # Enable testing mode
    TESTING = True
    # Test-specific settings can be added here