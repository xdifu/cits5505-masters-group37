"""
This Selenium test case is designed to verify the visualization page of a Flask-based web application.

Summary of Logic:
1. The `setUpClass` method initializes a test-specific Flask application with an in-memory database,
   creates a test user, and starts the Flask app in a separate thread.
2. The `setUp` method configures the Chrome WebDriver and performs user login using the test user's credentials.
3. The `test_visualization_elements` method navigates to the /visualization page and waits for the page to load.
   - It checks if the header text "Sentiment Analytics Dashboard" is present.
   - It verifies that the three expected charts (barChart, pieChart, and lineChart) are present and visible on the page.
4. The `tearDown` method cleanly shuts down the WebDriver after each test.
5. The `tearDownClass` method cleans up the database and application context.

Purpose:
Ensure that the visualization page is correctly rendered, all major chart elements are loaded,
and the user is authenticated beforehand, all within an isolated test environment.
"""
import unittest
import threading
import time
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

class TestVisualizationPage(unittest.TestCase):
    flask_app = None
    app_context = None
    app_thread = None
    flask_port = 5004 # Using a unique port for this test class
    test_user_username = "vis_test_user"
    test_user_password = "TestPassword123!"

    @classmethod
    def setUpClass(cls):
        # Create a Flask app instance with TestingConfig
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
            kwargs={"port": cls.flask_port, "use_reloader": False, "debug": False}
        )
        cls.app_thread.daemon = True # Use daemon attribute
        cls.app_thread.start()
        time.sleep(2)  # Wait for the server to start

    @classmethod
    def tearDownClass(cls):
        # Clean up the database and app context
        if cls.app_context:
            db.session.remove()
            db.drop_all()
            cls.app_context.pop()
        # The daemon app_thread will stop when the main process exits.

    def setUp(self):
        # Initialize browser
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Run headless for CI/automated environments
        chrome_options.add_argument("--window-size=1920,1080") # Define window size
        chrome_options.add_argument("--disable-gpu") # Recommended for headless
        chrome_options.add_argument("--no-sandbox") # Recommended for headless in Docker/Linux
        chrome_options.add_argument("--disable-dev-shm-usage") # Recommended for headless in Docker/Linux

        service = Service() # Assumes chromedriver is in PATH or service is configured
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5) # Implicit wait for element location
        self.base_url = f"http://127.0.0.1:{self.flask_port}"
        self.wait = WebDriverWait(self.driver, 10) # Explicit wait for conditions

        # Login first using the programmatically created user
        self.driver.get(f"{self.base_url}/auth/login")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.test_user_username)
        self.driver.find_element(By.NAME, "password").send_keys(self.test_user_password)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))).click()

        # Wait for redirection to the index page to confirm login
        self.wait.until(EC.url_contains("/index"))

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_visualization_elements(self):
        driver = self.driver
        driver.get(f"{self.base_url}/visualization")

        # Wait for the main heading of the visualization page
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Sentiment Analytics Dashboard')]"))
        )
        # Verify the page title is present in the source
        self.assertIn("Sentiment Analytics Dashboard", driver.page_source)

        # Verify that the three expected chart canvas elements are present
        bar_chart = self.wait.until(EC.presence_of_element_located((By.ID, "barChart")))
        pie_chart = self.wait.until(EC.presence_of_element_located((By.ID, "pieChart")))
        line_chart = self.wait.until(EC.presence_of_element_located((By.ID, "lineChart")))

        # Check if charts are displayed (basic check, actual rendering is by JS)
        self.assertTrue(bar_chart.is_displayed(), "Bar chart canvas should be displayed.")
        self.assertTrue(pie_chart.is_displayed(), "Pie chart canvas should be displayed.")
        self.assertTrue(line_chart.is_displayed(), "Line chart canvas should be displayed.")

if __name__ == '__main__':
    unittest.main()