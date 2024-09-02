"""
Test module for the database service.

This module contains unit tests for the database service functions,
including initialization, retrieval, and error handling of the Pinecone database connection.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.services.database.db_service import init_db, get_db, pinecone_manager

@pytest.fixture
def app():
    """
    Create and configure a test Flask application.

    Returns:
        Flask: The configured test Flask application.
    """
    app = Flask(__name__)
    app.config['PINECONE_API_KEY'] = 'test_api_key'
    app.config['PINECONE_ENVIRONMENT'] = 'test_environment'
    app.config['PINECONE_INDEX_NAME'] = 'test_index'
    return app

def test_init_db_success(app):
    """
    Test successful initialization of the database.

    This test ensures that the PineconeManager is called with the correct parameters
    and that the global pinecone_manager is set after initialization.

    Args:
        app (Flask): The test Flask application.
    """
    with patch('app.services.database.db_service.PineconeManager') as mock_pinecone_manager:
        init_db(app)
        mock_pinecone_manager.assert_called_once_with(
            api_key='test_api_key',
            environment='test_environment',
            index_name='test_index'
        )
        assert pinecone_manager is not None

def test_get_db_failure(app):
    """
    Test get_db failure when initialization fails.

    This test ensures that get_db raises a RuntimeError when
    database initialization fails.

    Args:
        app (Flask): The test Flask application.
    """
    global pinecone_manager
    pinecone_manager = None
    
    with patch('app.services.database.db_service.init_db', side_effect=Exception("Test error")), \
         patch('app.services.database.db_service.current_app', return_value=app):
        with pytest.raises(RuntimeError) as exc_info:
            get_db()
        assert "Pinecone manager initialization failed" in str(exc_info.value)

    assert pinecone_manager is None

def test_get_db_success(app):
    """
    Test successful retrieval of the database connection.

    This test ensures that get_db returns the initialized PineconeManager instance.

    Args:
        app (Flask): The test Flask application.
    """
    global pinecone_manager
    pinecone_manager = None
    with patch('app.services.database.db_service.PineconeManager') as mock_pinecone_manager:
        mock_instance = MagicMock()
        mock_pinecone_manager.return_value = mock_instance
        
        with app.app_context():
            db = get_db()
        
        assert db == mock_instance

def test_get_db_initialization(app):
    """
    Test that get_db initializes the database if it's not already initialized.

    This test ensures that get_db calls init_db to initialize
    the database if it hasn't been initialized yet.

    Args:
        app (Flask): The test Flask application.
    """
    global pinecone_manager
    pinecone_manager = None
    
    with patch('app.services.database.db_service.init_db') as mock_init_db, \
         patch('app.services.database.db_service.current_app', return_value=app):
        db = get_db()
    
        mock_init_db.assert_called_once_with(app)
        assert db == pinecone_manager

def test_get_db_failure(app):
    """
    Test get_db failure when initialization fails.

    This test ensures that get_db raises a RuntimeError when
    database initialization fails.

    Args:
        app (Flask): The test Flask application.
    """
    global pinecone_manager
    pinecone_manager = None
    
    with patch('app.services.database.db_service.init_db', side_effect=Exception("Test error")):
        with app.app_context():
            with pytest.raises(RuntimeError) as exc_info:
                get_db()
            assert "Pinecone manager initialization failed" in str(exc_info.value)

    assert pinecone_manager is None