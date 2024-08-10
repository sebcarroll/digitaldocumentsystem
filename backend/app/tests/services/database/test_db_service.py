"""Test module for the database service."""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.services.database.db_service import init_db, get_db, pinecone_manager
from app.services.database.pinecone_manager_service import PineconeManager

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = Flask(__name__)
    app.config['PINECONE_API_KEY'] = 'test_api_key'
    app.config['PINECONE_ENVIRONMENT'] = 'test_environment'
    app.config['PINECONE_INDEX_NAME'] = 'test_index'
    app.config['OPENAI_API_KEY'] = 'test_openai_key'
    return app

def test_init_db_success(app):
    """Test successful initialization of the database."""
    with patch('app.services.database.db_service.PineconeManager') as mock_pinecone_manager:
        init_db(app)
        mock_pinecone_manager.assert_called_once_with(
            api_key='test_api_key',
            environment='test_environment',
            index_name='test_index',
            openai_api_key='test_openai_key'
        )
        assert pinecone_manager is not None

def test_init_db_failure(app):
    """Test database initialization failure."""
    global pinecone_manager
    pinecone_manager = None
    with patch('app.services.database.db_service.PineconeManager', side_effect=Exception("Test error")):
        with pytest.raises(Exception, match="Test error"):
            init_db(app)
    assert pinecone_manager is None

def test_get_db_success(app):
    """Test successful retrieval of the database connection."""
    global pinecone_manager
    pinecone_manager = None
    with patch('app.services.database.db_service.PineconeManager') as mock_pinecone_manager:
        mock_instance = MagicMock()
        mock_pinecone_manager.return_value = mock_instance
        
        with app.app_context():
            db = get_db()
        
        assert db == mock_instance

def test_init_db_logging(app, caplog):
    """Test logging during database initialization."""
    with patch('app.services.database.db_service.PineconeManager'):
        init_db(app)
        
    assert "Initializing Pinecone manager" in caplog.text
    assert "PINECONE_API_KEY: set" in caplog.text
    assert "PINECONE_ENVIRONMENT: test_environment" in caplog.text
    assert "PINECONE_INDEX_NAME: test_index" in caplog.text
    assert "OPENAI_API_KEY: set" in caplog.text
    assert "Pinecone manager initialized successfully" in caplog.text

def test_init_db_failure_logging(app, caplog):
    """Test logging during database initialization failure."""
    with patch('app.services.database.db_service.PineconeManager', side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            init_db(app)
        
    assert "Failed to initialize Pinecone manager: Test error" in caplog.text

def test_get_db_warning_logging(app, caplog):
    """Test warning logging when getting an uninitialized database connection."""
    global pinecone_manager
    pinecone_manager = None
    
    with patch('app.services.database.db_service.PineconeManager'):
        with app.app_context():
            get_db()
        
    assert "Pinecone manager is None, initializing..." in caplog.text