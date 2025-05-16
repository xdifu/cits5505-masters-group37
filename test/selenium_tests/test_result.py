"""
Selenium Test: Result Page Navigation

This test suite verifies the navigation functionality from the results page.

Test Overview:
--------------
- A test-specific Flask application instance is created with an in-memory SQLite database.
- A test user and a sample analysis report are created programmatically for this test class.
- The test logs in as the created test user.
- It navigates to the /results page.
- It verifies that "View Dashboard" and "Share Report" buttons are present for a report.
- It clicks these buttons and asserts that the navigation to the correct URLs (/results_dashboard and /share_report) occurs.
- The test runs in an isolated environment, ensuring no interference from or to other tests.
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
from app.models import User, AnalysisReport # Assuming your models are User and AnalysisReport
from app.config import TestingConfig

class TestResultPageNavigation(unittest.TestCase): # Renamed class for clarity
    flask_app = None
    app_context = None
    app_thread = None
    test_user_username = "result_test_user"
    test_user_password = "TestPassword123!"
    test_report_name = "Sample Test Report"

    @classmethod
    def setUpClass(cls):
        # Create a Flask app instance with TestingConfig
        cls.flask_app = create_app(TestingConfig)
        # Establish an application context
        cls.app_context = cls.flask_app.app_context()
        cls.app_context.push()
        # Create all database tables
        db.create_all()

        # Create a test user
        user = User.query.filter_by(username=cls.test_user_username).first()
        if not user:
            user = User(username=cls.test_user_username, email=f"{cls.test_user_username}@example.com")
            user.set_password(cls.test_user_password)
            db.session.add(user)
            db.session.commit()
        cls.user_id = user.id # Store user_id for creating reports

        # Create a sample analysis report for the test user
        report = AnalysisReport.query.filter_by(name=cls.test_report_name, user_id=cls.user_id).first()
        if not report:
            report = AnalysisReport(
                name=cls.test_report_name,
                user_id=cls.user_id,
                # Add other necessary fields for a valid report, e.g., timestamp
                # Assuming timestamp is auto-set or not strictly needed for navigation test
            )
            db.session.add(report)
            db.session.commit()


        # Start the test-specific Flask app in a separate thread
        cls.app_thread = threading.Thread(
            target=cls.flask_app.run,
            kwargs={"port": 5002, "use_reloader": False, "debug": False} # Use a different port
        )
        cls.app_thread.daemon = True
        cls.app_thread.start()
        time.sleep(2)  # Wait for the server to start

    @classmethod
    def tearDownClass(cls):
        if cls.app_context:
            db.session.remove()
            db.drop_all()
            cls.app_context.pop()

    def setUp(self):
        # Initialize browser
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920,1080") # Uncomment for non-headless debugging
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10) # Implicit wait
        self.base_url = "http://127.0.0.1:5002" # Match port from setUpClass
        self.wait = WebDriverWait(self.driver, 10) # Explicit wait

        # Login the test user
        self.driver.get(f"{self.base_url}/auth/login")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.test_user_username)
        self.driver.find_element(By.NAME, "password").send_keys(self.test_user_password)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))).click()
        self.wait.until(EC.url_contains("/index")) # Verify login success

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_result_buttons_navigation(self):
        driver = self.driver
        driver.get(f"{self.base_url}/results")

        # Wait until the page loads and at least one report card is visible
        # This assumes your report cards have a common, identifiable class like "report-card"
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "report-card"))
        )

        # Click the first "View Dashboard" button
        # Using a more robust XPath to find the link within a report card context if needed,
        # or assuming LINK_TEXT is unique enough for the first report.
        view_buttons = driver.find_elements(By.LINK_TEXT, "VIEW DASHBOARD")
        self.assertTrue(view_buttons, "View Dashboard button not found on the results page.")
        view_buttons[0].click() # Click the first one found
        self.wait.until(EC.url_contains("/results_dashboard")) # Wait for URL to change
        self.assertIn("/results_dashboard", driver.current_url, "Navigation to results_dashboard failed.")

        driver.back() # Navigate back to the results page
        self.wait.until(EC.url_contains("/results")) # Ensure back navigation is complete
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "report-card"))) # Wait for cards to reappear

        # Click the first "Share Report" button
        share_buttons = driver.find_elements(By.LINK_TEXT, "SHARE REPORT")
        self.assertTrue(share_buttons, "Share Report button not found on the results page.")
        share_buttons[0].click() # Click the first one found
        self.wait.until(EC.url_contains("/share_report")) # Wait for URL to change
        self.assertIn("/share_report", driver.current_url, "Navigation to share_report failed.")

if __name__ == '__main__':
    unittest.main()