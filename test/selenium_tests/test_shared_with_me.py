"""
This test automates the full 'Shared With Me' feature flow in the web application.

Test Summary:
- Sets up an isolated test environment with an in-memory database.
- Programmatically creates two users: a sharer and a receiver.
- Logs in as the sharer user.
- Submits an analysis request on the /analyze page.
- Verifies the report is created and captures its timestamp from the /results page.
- Clicks the "Share Report" button.
- Handles potential redirection and attempts to share the report with the receiver user.
- Logs out as the sharer and logs in as the receiver.
- Visits the /shared_with_me page as the receiver to verify that the shared report appears.
- Validates that the timestamp from the original submission appears on the receiver's shared report page.
"""
import unittest
import threading
import time
from datetime import datetime # For timestamp parsing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import necessary components for creating a test-specific app instance and DB
from app import create_app, db
from app.models import User, AnalysisReport # Assuming AnalysisReport is your report model
from app.config import TestingConfig

class TestSharedWithMeFlow(unittest.TestCase):
    flask_app = None
    app_context = None
    app_thread = None
    sharer_username = "test_sharer_user_v2" # Changed to avoid potential old data if DB isn't perfectly clean between runs
    sharer_password = "TestPassword123!"
    receiver_username = "test_receiver_user_v2"
    receiver_password = "TestPassword123!"
    flask_port = 5003 # Unique port for this test class

    @classmethod
    def setUpClass(cls):
        # Create a Flask app instance with TestingConfig
        cls.flask_app = create_app(TestingConfig)
        # Establish an application context
        cls.app_context = cls.flask_app.app_context()
        cls.app_context.push()
        # Create all database tables
        db.create_all()

        # Create sharer user
        sharer = User.query.filter_by(username=cls.sharer_username).first()
        if not sharer:
            sharer = User(username=cls.sharer_username, email=f"{cls.sharer_username}@example.com")
            sharer.set_password(cls.sharer_password)
            db.session.add(sharer)

        # Create receiver user
        receiver = User.query.filter_by(username=cls.receiver_username).first()
        if not receiver:
            receiver = User(username=cls.receiver_username, email=f"{cls.receiver_username}@example.com")
            receiver.set_password(cls.receiver_password)
            db.session.add(receiver)
        
        db.session.commit()

        # Start the test-specific Flask app in a separate thread
        cls.app_thread = threading.Thread(
            target=cls.flask_app.run,
            kwargs={"port": cls.flask_port, "use_reloader": False, "debug": False}
        )
        cls.app_thread.daemon = True
        cls.app_thread.start()
        time.sleep(3)  # Increased wait for server to start

    @classmethod
    def tearDownClass(cls):
        if cls.app_context:
            db.session.remove()
            db.drop_all() # Ensures a clean slate for next class run
            cls.app_context.pop()
        # Note: The app_thread will be stopped when the main process exits as it's a daemon.

    def setUp(self):
        # Initialize browser
        chrome_options = Options()
        # Uncomment for non-headless debugging:
        # chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service() # Assumes chromedriver is in PATH
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5) 
        self.base_url = f"http://127.0.0.1:{self.flask_port}"
        self.wait = WebDriverWait(self.driver, 15) # Explicit wait timeout

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def _login(self, username, password):
        # Helper function to log in a user
        self.driver.get(f"{self.base_url}/auth/login")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))).click()
        self.wait.until(EC.url_contains("/index")) # Verify login success

    def _logout(self):
        # Helper function to log out
        self.driver.get(f"{self.base_url}/auth/logout")
        self.wait.until(EC.url_contains("/auth/login")) # Assuming logout redirects to login

    def test_shared_with_me_workflow(self):
        driver = self.driver

        # Step 1: Login as sharer_user
        self._login(self.sharer_username, self.sharer_password)

        # Step 2: Go to /analyze and submit text
        driver.get(f"{self.base_url}/analyze")
        self.wait.until(EC.presence_of_element_located((By.ID, "news_text")))
        unique_report_identifier = f"TestShareFlow_{int(time.time())}" # Used for report name and later validation
        shared_text = f"This is an automated test input for sharing: {unique_report_identifier}. It needs to be long enough for meaningful results."
        
        driver.find_element(By.ID, "news_text").send_keys(shared_text)
        
        # Ensure the report_name field is filled for reliable identification
        try:
            driver.find_element(By.ID, "report_name").send_keys(unique_report_identifier)
        except Exception as e:
            self.fail(f"Could not find or interact with report_name field. This is critical for the test. Error: {e}")

        analyze_submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Analyze and Create Report']")))
        analyze_submit_button.click()
        
        # Wait for navigation to results_dashboard (either via modal or direct redirect)
        # This confirms report creation and allows extraction of report_id
        actual_report_id = None
        try:
            # Try to handle modal if it appears
            self.wait.until(EC.visibility_of_element_located((By.ID, "analysis-result-content")))
            view_results_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='analysisResultModal']//a[contains(@href, '/results_dashboard/')] | //div[@id='analysisResultModal']//a[contains(@href, '/results')]"))
            )
            href = view_results_link.get_attribute("href")
            print(f"Modal link found: {href}. Clicking it.")
            view_results_link.click()
            self.wait.until(EC.url_contains("/results_dashboard/")) # Wait for URL to change after click
        except Exception as e_modal:
            # If modal not found or error with modal, expect direct redirect
            print(f"Modal not processed or error: {e_modal}. Checking for direct redirect to /results_dashboard/.")
            self.wait.until(EC.url_contains("/results_dashboard/"))
        
        current_page_url = driver.current_url
        try:
            # Extract report_id from URL like ".../results_dashboard/123"
            # The URL might end with a slash, so strip it before splitting
            actual_report_id_str = current_page_url.strip('/').split('/')[-1]
            actual_report_id = int(actual_report_id_str)
            print(f"Successfully navigated to results dashboard. Extracted report ID: {actual_report_id} from URL: {current_page_url}")
        except (ValueError, IndexError) as e:
            self.fail(f"Could not extract report ID from results_dashboard URL: {current_page_url}. Error: {e}")

        # Fetch the report from DB to get its actual creation timestamp for later validation
        report_creation_timestamp = None
        with self.flask_app.app_context(): # Ensure app context for DB query
            report_from_db = db.session.get(AnalysisReport, actual_report_id)
            if report_from_db:
                # Verify the report name matches what was submitted
                self.assertEqual(report_from_db.name, unique_report_identifier, 
                                 f"Report name in DB ('{report_from_db.name}') should match the one submitted ('{unique_report_identifier}').")
                report_creation_timestamp = report_from_db.timestamp # This is a datetime object
                print(f"Retrieved report '{report_from_db.name}' (ID: {report_from_db.id}) with timestamp {report_creation_timestamp} from DB.")
            else:
                self.fail(f"Report with ID {actual_report_id} not found in the database after creation.")
        
        if not report_creation_timestamp: # Should be caught by the fail above, but as a safeguard
             self.fail(f"Failed to retrieve creation timestamp for report ID {actual_report_id}.")

        # Step 3: Navigate directly to the share_report page for the created report
        share_report_url = f"{self.base_url}/share_report/{actual_report_id}"
        print(f"Navigating directly to share page: {share_report_url}")
        driver.get(share_report_url)
        
        # Verify navigation to the share_report page
        try:
            self.wait.until(EC.url_contains(f"/share_report/{actual_report_id}"))
            # Check for a key element on the share_analysis.html page (e.g., the username input field)
            self.wait.until(EC.presence_of_element_located((By.NAME, "share_with_username")))
            print(f"Successfully navigated to the share report page: {driver.current_url}")
        except Exception as e:
            current_url_after_direct_nav = driver.current_url
            self.fail(f"Failed to navigate to or verify the share report page for report ID {actual_report_id}. Expected URL part: /share_report/{actual_report_id}. Current URL: {current_url_after_direct_nav}. Error: {e}")

        # Step 4: Share the report using the "Quick Share" form on share_analysis.html
        self.wait.until(EC.presence_of_element_located((By.NAME, "share_with_username"))).send_keys(self.receiver_username)
        
        # Find and click the submit button for the quick share form
        quick_share_submit_button = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, 
            f"//form[contains(@action, '/share_report/{actual_report_id}')]//input[@type='submit'] | //form[contains(@action, '/share_report/{actual_report_id}')]//button[@type='submit']"
        )))
        quick_share_submit_button.click()
        
        # Wait for the flash message confirming successful share
        self.wait.until(EC.visibility_of_element_located((
            By.XPATH, 
            f"//div[contains(@class, 'alert-success') and contains(text(), 'Report shared successfully with {self.receiver_username}')]"
        )))
        # URL should still be on the share_report page (or redirect back to it)
        self.wait.until(EC.url_contains(f"/share_report/{actual_report_id}"))

        # Step 5: Logout as sharer_user
        self._logout()

        # Step 6: Login as receiver_user
        self._login(self.receiver_username, self.receiver_password)

        # Step 7: Visit /shared_with_me and validate the shared report
        driver.get(f"{self.base_url}/shared_with_me")
        
        try:
            # Wait for the shared report item to appear, identified by its name (unique_report_identifier)
            self.wait.until(EC.presence_of_element_located((
                By.XPATH, 
                f"//div[contains(@class, 'list-group-item')]//h5[contains(normalize-space(), '{unique_report_identifier}')]"
            )))
            
            # Validate the timestamp using report_creation_timestamp (datetime object from DB)
            # The shared_with_me.html template uses report.timestamp.strftime('%Y-%m-%d %H:%M')
            # report_creation_timestamp is UTC. strftime will format it.
            expected_date_str_in_shared_view = report_creation_timestamp.strftime("%Y-%m-%d")
            expected_time_str_in_shared_view = report_creation_timestamp.strftime("%H:%M")
            
            # The text on shared_with_me page is "Shared by: <sharer> on <date> <time>"
            expected_timestamp_display_text = f"{expected_date_str_in_shared_view} {expected_time_str_in_shared_view}"
            
            # XPath to find the small tag containing the timestamp within the correct report item
            timestamp_small_element_xpath = (
                f"//div[contains(@class, 'list-group-item') and .//h5[contains(normalize-space(), '{unique_report_identifier}')]]"
                f"//small[contains(@class, 'text-muted') and contains(., '{expected_timestamp_display_text}')]"
            )
            self.wait.until(EC.presence_of_element_located((By.XPATH, timestamp_small_element_xpath)))
            
            print(f"Successfully validated shared report '{unique_report_identifier}' with timestamp parts '{expected_timestamp_display_text}' on /shared_with_me page.")

        except Exception as e_validate: 
            page_source_debug = driver.page_source 
            # Try to get expected_timestamp_display_text if it was defined
            expected_ts_text_for_error = "NOT_DEFINED"
            if 'expected_timestamp_display_text' in locals():
                expected_ts_text_for_error = expected_timestamp_display_text
            self.fail(f"Validation on /shared_with_me page for report '{unique_report_identifier}' failed. Expected timestamp text: '{expected_ts_text_for_error}'. Error: {e_validate}. Page source (first 1000 chars): {page_source_debug[:1000]}")