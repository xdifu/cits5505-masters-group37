import pytest
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import url_for
from app import create_app, db
from app.models import User
from config import TestingConfig
import os

# Fixture to manage the Flask app and server
@pytest.fixture(scope='session')
def live_server_url():
    """Starts the Flask development server for Selenium tests."""
    app = create_app(TestingConfig)
    app.config['SERVER_NAME'] = 'localhost:5000'  # Ensure SERVER_NAME is set for url_for
    
    # Use a separate thread for the Flask server
    def run_server():
        # Set FLASK_ENV to testing to use TestingConfig when run.py is executed
        os.environ['FLASK_ENV'] = 'testing'
        # Use the app instance configured with TestingConfig
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Allow main thread to exit even if server thread is running
    server_thread.start()
    
    # Wait for the server to start
    time.sleep(2) # Give the server a moment to start

    yield "http://localhost:5000" # Base URL for tests

    # Teardown: No explicit server stop needed due to daemon thread

@pytest.fixture(scope='session')
def browser():
    """Provides a Selenium WebDriver instance."""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode for CI/CD
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10) # Global implicit wait
    yield driver
    driver.quit()

@pytest.fixture(scope='function')
def setup_database(live_server_url): # Depends on live_server_url to ensure app context
    """Sets up and tears down the database for each test function."""
    app = create_app(TestingConfig) # Create a new app instance for db operations
    with app.app_context():
        db.drop_all()  # Ensure a clean slate by dropping tables first
        db.create_all() # Create all tables based on models
        # Create a default user for login tests if needed
        if not User.query.filter_by(username='testuser_selenium').first():
            user = User(username='testuser_selenium', email='selenium@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        yield db # Provide the db session to the tests

class TestSeleniumAuth:
    def test_register_and_login(self, browser, live_server_url, setup_database):
        """Test user registration and login functionality."""
        # Registration
        browser.get(f"{live_server_url}/auth/register")
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("newseleniumuser")
        browser.find_element(By.NAME, "email").send_keys("newselenium@example.com")
        browser.find_element(By.NAME, "password").send_keys("securepassword")
        browser.find_element(By.NAME, "password2").send_keys("securepassword")
        
        register_submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/auth/register']//input[@type='submit']"))
        )
        register_submit_button.click()

        # Check for successful registration flash message
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Congratulations, you are now a registered user!')]"))
        )

        # Login
        browser.get(f"{live_server_url}/auth/login")
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("newseleniumuser")
        browser.find_element(By.NAME, "password").send_keys("securepassword")

        login_submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/auth/login']//input[@type='submit']"))
        )
        login_submit_button.click()

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))
        assert "Logout" in browser.page_source

    def test_login_logout(self, browser, live_server_url, setup_database):
        """Test login and logout functionality with a pre-existing user."""
        # Login
        browser.get(f"{live_server_url}/auth/login")
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("testuser_selenium")
        browser.find_element(By.NAME, "password").send_keys("password123")
        
        login_submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/auth/login']//input[@type='submit']"))
        )
        login_submit_button.click()

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))
        assert "Logout" in browser.page_source

        # Logout
        logout_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        )
        logout_link.click()
        
        WebDriverWait(browser, 10).until(EC.url_contains(f"{live_server_url}/auth/login"))
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        assert "Login" in browser.title

class TestSeleniumMainFeatures:
    def test_navigate_to_analyze_page_and_submit(self, browser, live_server_url, setup_database):
        """Test navigation to the analyze page and submitting text for analysis."""
        # First, log in
        browser.get(f"{live_server_url}/auth/login")
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("testuser_selenium")
        browser.find_element(By.NAME, "password").send_keys("password123")
        
        login_submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/auth/login']//input[@type='submit']"))
        )
        login_submit_button.click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))

        # Navigate to Analyze page
        analyze_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Analyze News"))
        )
        analyze_link.click()
        
        WebDriverWait(browser, 10).until(EC.url_contains(f"{live_server_url}/analyze"))
        assert "Analyze News Text" in browser.title

        # Submit text for analysis
        text_area = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "news_text"))
        )
        text_area.send_keys("This is a test news article for Selenium.")
        
        submit_button_analyze = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/analyze']//input[@type='submit' and @value='Analyze']"))
        )
        submit_button_analyze.click()

        # Check for analysis results (this will depend on how results are displayed)
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.ID, "analysis-results"))
        )
        assert "Analysis Results" in browser.page_source

    def test_view_results_dashboard(self, browser, live_server_url, setup_database):
        """Test viewing the results dashboard after logging in."""
        current_db = setup_database

        # Log in
        browser.get(f"{live_server_url}/auth/login")
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("testuser_selenium")
        browser.find_element(By.NAME, "password").send_keys("password123")
        
        login_submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@action='/auth/login']//input[@type='submit']"))
        )
        login_submit_button.click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))

        # Create a dummy result using the fixture's db session
        user = current_db.session.query(User).filter_by(username='testuser_selenium').first()
        if not user:
            pytest.fail("Default selenium user 'testuser_selenium' not found in the database.")

        from app.models import AnalysisReport
        from datetime import datetime, timezone
        
        report = AnalysisReport(
            original_text="Selenium test report content",
            sentiment="Neutral",
            author_id=user.id,
            timestamp=datetime.now(timezone.utc)
        )
        current_db.session.add(report)
        current_db.session.commit()
        
        results_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "My Results"))
        )
        results_link.click()

        WebDriverWait(browser, 10).until(EC.url_contains(f"{live_server_url}/results"))
        assert "My Analysis Results" in browser.title
        assert "Selenium test report content" in browser.page_source
