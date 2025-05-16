"""
This Selenium test suite verifies the registration functionality of the web application.

Test Overview:
--------------
- The test navigates to the user registration page (/auth/register).
- It waits for the registration form to load by checking for the presence of the username input field.
- A random username is generated using UUID to avoid duplicates during testing.
- A secure password is defined that meets common validation rules (uppercase, lowercase, number, special character).
- The test fills out the registration form with:
    * Random username
    * Random email
    * Password and confirmation
- It then submits the form by clicking the submit button.
- After submission, the test checks that the page redirects to the login page,
  confirming that registration was successful.

"""
import unittest
import uuid
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
from app.config import TestingConfig

class TestRegistrationFlow(unittest.TestCase):

    def setUp(self):
        # Create a Flask app instance with TestingConfig (uses in-memory SQLite)
        self.flask_app = create_app(TestingConfig)
        # Establish an application context
        self.app_context = self.flask_app.app_context()
        self.app_context.push()
        # Create all database tables
        db.create_all()

        # Start the test-specific Flask app in a separate thread
        self.app_thread = threading.Thread(
            target=self.flask_app.run,
            kwargs={"port": 5000, "use_reloader": False, "debug": False} # Ensure a unique port or manage ports if running parallel
        )
        self.app_thread.daemon = True
        self.app_thread.start()
        time.sleep(2)  # Wait a bit longer for the server with new DB to start

        # Initialize browser
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        # Optional: Remove headless for debugging
        # chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5) # Implicit wait for element location
        self.base_url = "http://127.0.0.1:5000"
        self.wait = WebDriverWait(self.driver, 10) # Explicit wait for conditions

    def test_register_user(self):
        driver = self.driver
        driver.get(f"{self.base_url}/auth/register")

        # Wait for the username field to be present
        self.wait.until(EC.presence_of_element_located((By.ID, "username")))

        random_username = f"selenium_{uuid.uuid4().hex[:8]}" # Increased randomness slightly
        random_email = f"{random_username}@example.com"
        secure_password = "TestPassword123!" # Ensure this meets your app's password policy

        # Fill the registration form
        # Assuming 'username' field has id="username" and name="username"
        driver.find_element(By.ID, "username").send_keys(random_username)
        # The line below was redundant if ID and NAME "username" point to the same element.
        # driver.find_element(By.NAME, "username").send_keys(random_username)
        driver.find_element(By.NAME, "email").send_keys(random_email)
        driver.find_element(By.NAME, "password").send_keys(secure_password)
        driver.find_element(By.NAME, "password2").send_keys(secure_password)

        # Click the submit button
        submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
        submit_button.click()

        # Wait for redirection to the login page and assert URL
        self.wait.until(EC.url_contains("/auth/login"))
        self.assertIn("/auth/login", driver.current_url.lower(), "Redirection to login page failed after registration.")

    def tearDown(self):
        if self.driver:
            self.driver.quit()

        # Clean up the database and app context
        if hasattr(self, 'app_context') and self.app_context:
            db.session.remove()
            db.drop_all()
            self.app_context.pop()

        # Note: Stopping the Flask app thread (self.app_thread) explicitly can be complex.
        # Since it's a daemon thread, it will terminate when the main test process exits.
        # For more controlled shutdown, the Flask app would need a shutdown endpoint or mechanism.

if __name__ == '__main__':
    unittest.main()