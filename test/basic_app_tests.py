# Simple Flask application test using Selenium
import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import create_app, db
from app.models import User

class TestingConfig:
    """Testing configuration - use a file-based database for consistent state."""
    TESTING = True
    SECRET_KEY = 'test-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test-selenium.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5000'

@pytest.fixture(scope='module')
def app():
    """Create and configure a Flask app for testing."""
    # Remove test database if it exists
    if os.path.exists('test-selenium.db'):
        os.unlink('test-selenium.db')
        
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    
    yield app
    
    # Clean up
    if os.path.exists('test-selenium.db'):
        os.unlink('test-selenium.db')

@pytest.fixture(scope='module')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture(scope='module')
def browser():
    """Create a browser instance for Selenium tests."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

# Integration tests (non-Selenium)
def test_home_page(client):
    """Test home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_register_page(client):
    """Test registration page loads."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_login_page(client):
    """Test login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

# Selenium tests for future implementation
# These are skipped by default until the app and testing environment are properly configured
@pytest.mark.skip(reason="Selenium tests require specific environment setup")
def test_selenium_login(browser, app):
    """Test login with Selenium.
    
    This is a placeholder showing how to structure the test for future implementation.
    """
    with app.test_server():
        # Navigate to login page
        browser.get('http://localhost:5000/auth/login')
        
        # Fill login form
        username_field = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys("testuser")
        
        password_field = browser.find_element(By.NAME, "password")
        password_field.send_keys("password123")
        
        # Submit form
        browser.execute_script("document.querySelector('form').submit()")
        
        # Check for successful login
        WebDriverWait(browser, 10).until(
            lambda d: "/auth/login" not in d.current_url
        )
        
        # Simple assertion
        assert "login" not in browser.current_url.lower()
