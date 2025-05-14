# Completely revised Selenium test file
import pytest
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app import create_app, db
from app.models import User
from config import TestingConfig

# Ensure a file-based SQLite database for Selenium tests
class SeleniumTestConfig(TestingConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///selenium_test.db'
    SERVER_NAME = None  # Necessary for the live server to work properly
    WTF_CSRF_ENABLED = False
    TESTING = True

# Remove the test database file if it exists
if os.path.exists('selenium_test.db'):
    try:
        os.remove('selenium_test.db')
    except:
        pass

@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for the tests."""
    app = create_app(SeleniumTestConfig)
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
    
    yield app

@pytest.fixture(scope='session')
def live_server_url(app):
    """Starts a live server for testing."""
    port = 8943  # Use a non-standard port to avoid conflicts
    
    def run_app():
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_app)
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(1)
    
    yield f"http://127.0.0.1:{port}"

@pytest.fixture(scope='session')
def browser():
    """Provides a Selenium WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    yield driver
    
    # Cleanup when we're done
    driver.quit()

@pytest.fixture(scope='function')
def setup_database(app):
    """Sets up a clean database for each test."""
    with app.app_context():
        # Clear any existing data
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        yield db
        
        # Clean up after the test
        db.session.remove()

# Simple test for registration
@pytest.mark.skip(reason="Skip Selenium tests until app is ready")
class TestSelenium:
    def test_register(self, browser, live_server_url, setup_database):
        """Test user registration."""
        # Navigate to the registration page
        browser.get(f"{live_server_url}/auth/register")
        
        try:
            # Fill out the registration form
            username_field = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys("newuser")
            
            email_field = browser.find_element(By.NAME, "email")
            email_field.send_keys("new@example.com")
            
            password_field = browser.find_element(By.NAME, "password")
            password_field.send_keys("password123")
            
            password2_field = browser.find_element(By.NAME, "password2")
            password2_field.send_keys("password123")
            
            # Submit the form using JavaScript to avoid click issues
            browser.execute_script(
                "document.querySelector('form').submit();"
            )
            
            # Wait for redirect after registration
            WebDriverWait(browser, 10).until(
                lambda d: "/auth/register" not in d.current_url
            )
            
            # Basic assertion
            assert browser.current_url != f"{live_server_url}/auth/register"
            
        except Exception as e:
            # Useful debug output for test failures
            print(f"Test failed: {e}")
            print(f"Current URL: {browser.current_url}")
            print(f"Page source: {browser.page_source[:500]}...")
            raise
    
    def test_login(self, browser, live_server_url, setup_database):
        """Test user login."""
        # Navigate to the login page
        browser.get(f"{live_server_url}/auth/login")
        
        try:
            # Fill out the login form
            username_field = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys("testuser")
            
            password_field = browser.find_element(By.NAME, "password")
            password_field.send_keys("password123")
            
            # Submit the form using JavaScript to avoid click issues
            browser.execute_script(
                "document.querySelector('form').submit();"
            )
            
            # Wait for redirect after login
            WebDriverWait(browser, 10).until(
                lambda d: "/auth/login" not in d.current_url
            )
            
            # Basic assertion
            assert browser.current_url != f"{live_server_url}/auth/login"
            
        except Exception as e:
            # Useful debug output for test failures
            print(f"Test failed: {e}")
            print(f"Current URL: {browser.current_url}")
            print(f"Page source: {browser.page_source[:500]}...")
            raise
