# A simplified Selenium test file to focus on basic authentication tests
import pytest
import threading
import time
import os
import signal
import subprocess
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app import create_app, db
from app.models import User
from config import TestingConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def flask_server():
    """Starts the Flask server as a subprocess and returns the process object"""
    logger.info("Starting Flask server subprocess...")
    
    # Get the path to run_for_testing.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    run_script = os.path.join(parent_dir, "run_for_testing.py")
    
    # Start the subprocess
    env = os.environ.copy()
    env["FLASK_ENV"] = "testing"
    flask_process = subprocess.Popen(
        [sys.executable, run_script],
        env=env,
        cwd=parent_dir
    )
    
    # Give the server time to start
    logger.info(f"Waiting for Flask server to start (PID: {flask_process.pid})...")
    time.sleep(5)
    
    # Check if server is running by making a request
    try:
        import requests
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            logger.info("Flask server is up and running!")
        else:
            logger.warning(f"Flask server responded with status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error checking Flask server: {e}")
    
    yield flask_process
    
    # Cleanup: Kill the Flask server
    logger.info("Stopping Flask server...")
    try:
        os.kill(flask_process.pid, signal.SIGTERM)
        flask_process.wait(timeout=5)
        logger.info("Flask server stopped")
    except:
        flask_process.terminate()
        logger.warning("Had to forcefully terminate Flask server")

@pytest.fixture(scope='session')
def browser():
    """Provides a Selenium WebDriver instance."""
    logger.info("Initializing Chrome WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless')  # Uncomment for headless testing
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(30)  # Increased from 10s to 30s
        driver.maximize_window()
        logger.info("Chrome WebDriver initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        pytest.fail(f"Could not initialize WebDriver: {e}")
    
    yield driver
    
    logger.info("Closing Chrome WebDriver...")
    driver.quit()

@pytest.fixture(scope='function')
def setup_database(live_server_url):
    """Sets up test user for each test."""
    app = create_app(TestingConfig)
    with app.app_context():
        # Create a test user for login tests
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        yield db
        # Cleanup
        db.session.remove()

class TestBasicAuth:
    """Very simple authentication tests."""
    
    def test_register_user(self, browser, live_server_url, setup_database):
        """Test user registration flow."""
        # Go to register page
        browser.get(f"{live_server_url}/auth/register")
        
        # Wait for and fill out registration form
        username_field = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys("newuser")
        
        email_field = browser.find_element(By.NAME, "email")
        email_field.send_keys("new@example.com")
        
        pw_field = browser.find_element(By.NAME, "password")
        pw_field.send_keys("newpassword")
        
        pw2_field = browser.find_element(By.NAME, "password2")
        pw2_field.send_keys("newpassword")
        
        # Submit form - use JavaScript to avoid potential click issues
        browser.execute_script("document.querySelector('form').submit();")
        
        # Check for success - ensure we've been redirected away from register page
        WebDriverWait(browser, 20).until(
            lambda d: "/auth/register" not in d.current_url
        )
        
        # Simple assertion that registration was successful
        assert "register" not in browser.current_url.lower()
    
    def test_login_user(self, browser, live_server_url, setup_database):
        """Test basic user login."""
        # Go to login page
        browser.get(f"{live_server_url}/auth/login")
        
        # Fill out login form
        username_field = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys("testuser")
        
        pw_field = browser.find_element(By.NAME, "password")
        pw_field.send_keys("password123")
        
        # Submit form using JavaScript
        browser.execute_script("document.querySelector('form').submit();")
        
        # Check for successful login
        WebDriverWait(browser, 20).until(
            lambda d: "/auth/login" not in d.current_url
        )
        
        # Simple assertion that login was successful
        assert "login" not in browser.current_url.lower()
