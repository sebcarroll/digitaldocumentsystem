import pytest
from main import create_app

@pytest.fixture
def app():
    """
    Fixture to create and configure the Flask application instance for testing.

    This fixture sets the application to testing mode and returns the app instance,
    which can be used in other tests that require access to the app context.
    """
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """
    Fixture to provide a test client for the Flask application.

    This fixture returns a test client that can be used to make requests to the 
    application during tests. It relies on the `app` fixture to ensure the application 
    is properly configured.
    """
    return app.test_client()
