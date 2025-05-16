"""
Selenium Test: Analyze Flow

This test simulates a user logging into the application and submitting text to be analyzed.
The steps covered in this test are:
1. Set up a test-specific Flask app with an in-memory database.
2. Create a dedicated test user for this test class.
3. Set up the Chrome driver in headless mode.
4. Log in with the test user credentials and confirm successful navigation to the index page.
5. Navigate to the Analyze page and wait for the text input field to be ready.
6. Enter a sample news text and submit it for analysis.
7. Wait for the results page to render, verifying that "Keywords" and "Sentiment" are present in the output.

The test ensures that:
- The login works with valid credentials for a programmatically created user.
- The Analyze form is accessible and functional.
- The backend processes input text and returns expected analysis results.
- The test runs in an isolated environment.
"""
import threading
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import necessary components for creating a test-specific app instance and DB
from app import create_app, db
from app.models import User # Assuming your User model is in app.models
from app.config import TestingConfig

# ---------------------- Analyze Flow Selenium Test ----------------------
class TestAnalyzeFlow(unittest.TestCase):
    flask_app = None
    app_context = None
    app_thread = None
    test_user_username = "analyze_test_user"
    test_user_password = "TestPassword123!"

    @classmethod
    def setUpClass(cls):
        # Create a Flask app instance with TestingConfig (uses in-memory SQLite)
        cls.flask_app = create_app(TestingConfig)
        # Establish an application context
        cls.app_context = cls.flask_app.app_context()
        cls.app_context.push()
        # Create all database tables
        db.create_all()

        # Create a test user for this class
        user = User.query.filter_by(username=cls.test_user_username).first()
        if not user:
            user = User(username=cls.test_user_username, email=f"{cls.test_user_username}@example.com")
            user.set_password(cls.test_user_password)
            db.session.add(user)
            db.session.commit()

        # Start the test-specific Flask app in a separate thread
        cls.app_thread = threading.Thread(
            target=cls.flask_app.run,
            kwargs={"port": 5001, "use_reloader": False, "debug": False} # Use a different port if running simultaneously with other tests
        )
        cls.app_thread.daemon = True # Use daemon attribute
        cls.app_thread.start()
        time.sleep(2)  # Wait a bit longer for the server with new DB to start

    @classmethod
    def tearDownClass(cls):
        # Clean up the database and app context
        if cls.app_context:
            db.session.remove()
            db.drop_all()
            cls.app_context.pop()
        # The daemon app_thread will stop when the main process exits.
        # For explicit stopping, a shutdown mechanism in the app would be needed.

    def setUp(self):
        # Initialize browser
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service() # Assumes chromedriver is in PATH or service is configured
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10) # Increased implicit wait
        self.base_url = "http://127.0.0.1:5001" # Match port from setUpClass
        self.wait = WebDriverWait(self.driver, 15) # Explicit wait for conditions

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_analyze_text_submission(self):
        driver = self.driver
        driver.get(f"{self.base_url}/auth/login")

        # Wait for username field to be present and fill login form
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.test_user_username)
        driver.find_element(By.NAME, "password").send_keys(self.test_user_password)

        # Wait for the login submit button to be clickable and then click
        login_submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
        login_submit_button.click()

        # Wait for redirection to the index page
        self.wait.until(EC.url_contains("/index"))

        # Navigate to the analyze page (already on index, can go directly)
        # driver.get(f"{self.base_url}/index") # This line is redundant if already on /index
        driver.get(f"{self.base_url}/analyze")

        # Wait for the news_text input field to be present and enter text
        news_text_field = self.wait.until(EC.presence_of_element_located((By.ID, "news_text"))) # Assuming ID is 'news_text'
        news_text_field.send_keys("This is a test input provided for the purpose of conducting analysis and drawing insights. It needs to be long enough for meaningful results.")

        # Wait for the analyze submit button to be clickable and then click
        analyze_submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Analyze and Create Report']")))
        analyze_submit_button.click()

        # Wait for the results to appear on the page
        # Check for a more specific element that indicates results are loaded
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Keywords:')] | //*[contains(text(), 'Sentiment:')]")))

        # Assert that key terms are present in the page source
        page_source_lower = driver.page_source.lower()
        self.assertIn("keywords:", page_source_lower, "Keywords section not found on the results page.")
        self.assertIn("sentiment:", page_source_lower, "Sentiment section not found on the results page.")

if __name__ == '__main__':
    unittest.main()