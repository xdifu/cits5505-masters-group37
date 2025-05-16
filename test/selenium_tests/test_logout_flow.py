"""
Selenium Test: Logout Flow and Session Invalidation

This test simulates a user logging in, accessing a protected page, logging out,
and then attempting to re-access the protected page to ensure session invalidation.

Test Steps:
1. Set up a test-specific Flask app with an in-memory database.
2. Create a dedicated test user for this test class.
3. Set up the Chrome driver in headless mode.
4. Log in with the test user credentials.
5. Navigate to a protected page (e.g., /analyze) and verify access.
6. Click the "Logout" link/button.
7. Verify redirection to the index page and the presence of a "logged out" flash message.
8. Attempt to navigate back to the protected page (/analyze).
9. Assert that the user is redirected to the login page, confirming session invalidation.
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
from app.models import User
from app.config import TestingConfig

class TestLogoutFlow(unittest.TestCase):
    flask_app = None
    app_context = None
    app_thread = None
    flask_port = 5005 # Using a unique port for this test class
    test_user_username = "logout_test_user"
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
        cls.app_thread.daemon = True
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
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service() # Assumes chromedriver is in PATH
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5)
        self.base_url = f"http://127.0.0.1:{self.flask_port}"
        self.wait = WebDriverWait(self.driver, 10)

        # Login the test user
        self.driver.get(f"{self.base_url}/auth/login")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.test_user_username)
        self.driver.find_element(By.NAME, "password").send_keys(self.test_user_password)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))).click()
        self.wait.until(EC.url_contains("/index")) # Verify login success by redirection to index

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_logout_and_session_invalidation(self):
        driver = self.driver

        # Step 1: Navigate to a protected page (e.g., /analyze) and verify access
        protected_page_url = f"{self.base_url}/analyze"
        driver.get(protected_page_url)
        # Wait for a known element on the /analyze page to ensure it loaded
        self.wait.until(EC.presence_of_element_located((By.ID, "news_text"))) # Assuming 'news_text' is the ID of the textarea in analyze.html
        self.assertIn("/analyze", driver.current_url, "Should be on the analyze page after login.")

        # Step 2: Click the "Logout" link/button
        try:
            logout_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Logout")))
        except:
            # Fallback if "Logout" text is not found, try a common CSS selector for logout in a navbar
            logout_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, '/auth/logout')] | //header//a[contains(@href, '/auth/logout')]")))
        
        logout_link.click()

        # Step 3: Verify redirection to the login page and the presence of flash messages.
        # After logout, user is redirected to /index. If /index is protected or redirects anonymous users,
        # they will be further redirected to /auth/login. We expect to land on /auth/login.
        self.wait.until(EC.url_contains("/auth/login")) # Wait to land on the login page
        self.assertIn("/auth/login", driver.current_url, "Should be redirected to login page after logout sequence.")
        
        # Verify the "You have been logged out." flash message on the login page
        # This message was flashed by the logout route.
        logout_flash_message = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-info') and contains(text(), 'You have been logged out.')]"))
        )
        self.assertTrue(logout_flash_message.is_displayed(), "Logout flash message ('You have been logged out.') not visible on the login page.")

        # Verify the "Please log in to access this page." flash message on the login page
        # This message is typically flashed by Flask-Login when @login_required redirects.
        # The class might vary based on how your base.html renders flashes with category 'message' or 'warning'.
        login_required_flash_message = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert') and contains(text(), 'Please log in to access this page.')]"))
        )
        self.assertTrue(login_required_flash_message.is_displayed(), "'Please log in to access this page.' flash message not visible on the login page.")

        # Step 4: Attempt to navigate to the protected page (/analyze) again
        driver.get(protected_page_url)

        # Step 5: Assert that the user is still on (or redirected back to) the login page
        self.wait.until(EC.url_contains("/auth/login")) # Should remain on or be sent back to login
        self.assertIn("/auth/login", driver.current_url, "Should be on login page when attempting to access a protected route after logout.")
        
        # Additionally, check for a login form element to be sure
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        print("Logout and session invalidation test completed successfully.")

if __name__ == '__main__':
    unittest.main()