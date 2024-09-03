import pytest
from main import create_app
'''
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
'''

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

'''
@pytest.fixture(scope="class")
def chrome_driver(request):
    """
    Fixture to provide a Selenium Chrome WebDriver.

    This fixture creates a Chrome WebDriver instance, attaches it to the test class,
    and ensures it's properly closed after the tests are complete.
    """
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=service, options=options)
    request.cls.driver = driver
    yield driver
    driver.quit()
'''