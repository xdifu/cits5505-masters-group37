"""
Basic Selenium test script that doesn't rely on pytest
Run this directly to verify Selenium and Flask are working together
"""
import os
import sys
import time
import subprocess
import signal
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Setup logging - use UTF-8 encoding to handle emoji characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('selenium_test.log', encoding='utf-8')
    ]
)
# Add a separate stream handler for console output that doesn't use emojis
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger(__name__)
logger.addHandler(console_handler)

# Define status symbols without emojis for console output
PASS = "[PASS]"
FAIL = "[FAIL]"

def start_flask_server():
    """Start the Flask server as a subprocess"""
    logger.info("Starting Flask server...")
    
    # Get the current directory
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
    logger.info(f"Flask server started with PID: {flask_process.pid}")
    time.sleep(5)  # Wait for server to start
    
    return flask_process

def setup_webdriver():
    """Initialize the Chrome WebDriver"""
    logger.info("Setting up Chrome WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless')  # Uncomment for headless mode
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(30)  # 30 second implicit wait
        driver.maximize_window()
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        return None

def run_tests(driver):
    """Run the basic Selenium tests"""
    success = True
    base_url = "http://localhost:5000"
    
    try:
        # Test 1: Check if the homepage loads
        logger.info("\n--- Test 1: Homepage ---")
        driver.get(base_url)
        logger.info(f"Loaded URL: {driver.current_url}")
        
        # Check title and content
        logger.info(f"Page title: {driver.title}")
        if "Welcome" in driver.page_source:
            logger.info("✅ Homepage contains 'Welcome'")
        else:
            logger.error("❌ Homepage doesn't contain 'Welcome'")
            success = False
        
        # Test 2: Check registration page
        logger.info("\n--- Test 2: Registration Page ---")
        driver.get(f"{base_url}/auth/register")
        logger.info(f"Loaded URL: {driver.current_url}")
        
        # Verify registration form exists
        try:
            form = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            logger.info("✅ Registration form found")
            
            # Check for form fields
            username_field = driver.find_element(By.NAME, "username")
            email_field = driver.find_element(By.NAME, "email")
            password_field = driver.find_element(By.NAME, "password")
            password2_field = driver.find_element(By.NAME, "password2")
            
            logger.info("✅ All registration form fields found")
        except Exception as e:
            logger.error(f"❌ Error finding registration form: {e}")
            success = False
        
        # Test 3: Check login page
        logger.info("\n--- Test 3: Login Page ---")
        driver.get(f"{base_url}/auth/login")
        logger.info(f"Loaded URL: {driver.current_url}")
        
        # Verify login form exists
        try:
            form = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            logger.info("✅ Login form found")
            
            # Check for form fields
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            
            logger.info("✅ All login form fields found")
        except Exception as e:
            logger.error(f"❌ Error finding login form: {e}")
            success = False
        
        # Test 4: Try to register a user
        logger.info("\n--- Test 4: User Registration ---")
        driver.get(f"{base_url}/auth/register")
        
        try:
            # Fill out the registration form
            username_field = driver.find_element(By.NAME, "username")
            username_field.clear()
            username_field.send_keys("testuser_selenium")
            
            email_field = driver.find_element(By.NAME, "email")
            email_field.clear()
            email_field.send_keys("testselenium@example.com")
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys("password123")
            
            password2_field = driver.find_element(By.NAME, "password2")
            password2_field.clear()
            password2_field.send_keys("password123")
              logger.info("Form filled out, attempting to submit...")
            
            # Try to find and click the submit button instead of using JavaScript submit
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_button.click()
                logger.info("Form submitted by clicking submit button")
            except Exception as submit_error:
                logger.error(f"Error clicking submit button: {submit_error}")
                # As a fallback, try to submit using JavaScript event
                driver.execute_script("document.querySelector('form').dispatchEvent(new Event('submit'));")
                logger.info("Form submitted via JavaScript event dispatch")
            
            # Wait for redirect or success message
            WebDriverWait(driver, 20).until(
                lambda d: "Congratulations" in d.page_source or "login" in d.current_url.lower()
            )
            logger.info("✅ Registration successful")
            
        except Exception as e:
            logger.error(f"❌ Error during registration: {e}")
            success = False
        
        # Test 5: Try to login with the registered user
        logger.info("\n--- Test 5: User Login ---")
        driver.get(f"{base_url}/auth/login")
        
        try:
            # Fill out the login form
            username_field = driver.find_element(By.NAME, "username")
            username_field.clear()
            username_field.send_keys("testuser_selenium")
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys("password123")
              logger.info("Login form filled out, attempting to submit...")
            
            # Try to find and click the submit button instead of using JavaScript submit
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_button.click()
                logger.info("Login form submitted by clicking submit button")
            except Exception as submit_error:
                logger.error(f"Error clicking login submit button: {submit_error}")
                # As a fallback, try to submit using form submission event
                driver.execute_script("document.querySelector('form').dispatchEvent(new Event('submit'));")
                logger.info("Login form submitted via JavaScript event dispatch")
            
            # Wait for redirect to homepage
            WebDriverWait(driver, 20).until(
                lambda d: "/auth/login" not in d.current_url
            )
            logger.info("✅ Login successful")
            
        except Exception as e:
            logger.error(f"❌ Error during login: {e}")
            success = False
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test failure: {e}")
        return False

if __name__ == "__main__":
    flask_process = None
    try:
        # Start Flask server
        flask_process = start_flask_server()
        
        # Set up WebDriver
        driver = setup_webdriver()
        if not driver:
            sys.exit(1)
        
        # Run tests
        try:
            success = run_tests(driver)
            if success:
                logger.info("\n🎉 All tests passed successfully!")
                sys.exit(0)
            else:
                logger.error("\n❌ Some tests failed. Check the log for details.")
                sys.exit(1)
        finally:
            # Close WebDriver
            driver.quit()
            
    finally:
        # Stop Flask server
        if flask_process:
            logger.info("Stopping Flask server...")
            try:
                os.kill(flask_process.pid, signal.SIGTERM)
                flask_process.wait(timeout=5)
                logger.info("Flask server stopped")
            except:
                flask_process.terminate()
                logger.info("Flask server terminated")
