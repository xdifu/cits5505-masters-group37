"""
Comprehensive Selenium test for the Flask application
"""
import os
import sys
import time
import subprocess
import signal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_flask_server():
    """Start the Flask server as a subprocess"""
    print("Starting Flask server...")
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Start the Flask process
    flask_process = subprocess.Popen(
        ["python", os.path.join(parent_dir, "run_for_testing.py")],
        cwd=parent_dir
    )
    
    # Give the server time to start
    time.sleep(5)
    print("Flask server started with PID:", flask_process.pid)
    return flask_process

def run_selenium_test():
    """Run Selenium tests against the Flask application"""
    print("\n=== Running Selenium Tests ===")
    try:
        # Initialize Chrome driver
        print("Setting up Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        print("Chrome WebDriver initialized successfully")
        
        # Test 1: Homepage
        print("\nTest 1: Checking homepage...")
        driver.get("http://localhost:5000/")
        assert "Welcome" in driver.page_source, "Homepage doesn't contain 'Welcome'"
        print("✅ Homepage test passed")
        
        # Test 2: Registration page
        print("\nTest 2: Checking registration page...")
        driver.get("http://localhost:5000/auth/register")
        assert "Register" in driver.page_source, "Registration page doesn't contain 'Register'"
        print("✅ Registration page test passed")
        
        # Test 3: Login page
        print("\nTest 3: Checking login page...")
        driver.get("http://localhost:5000/auth/login")
        assert "Login" in driver.page_source, "Login page doesn't contain 'Login'"
        print("✅ Login page test passed")
        
        # Test 4: Test registration flow
        print("\nTest 4: Testing user registration...")
        driver.get("http://localhost:5000/auth/register")
        
        # Fill out registration form
        driver.find_element(By.NAME, "username").send_keys("testuser123")
        driver.find_element(By.NAME, "email").send_keys("testuser123@example.com")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "password2").send_keys("password123")
        
        # Submit using JavaScript (more reliable than clicking)
        driver.execute_script("document.querySelector('form').submit()")
        
        # Wait for redirect or success message
        WebDriverWait(driver, 30).until(
            lambda d: "Congratulations" in d.page_source or "login" in d.current_url.lower()
        )
        print("✅ Registration flow test passed")
        
        # Test 5: Test login flow
        print("\nTest 5: Testing user login...")
        driver.get("http://localhost:5000/auth/login")
        
        driver.find_element(By.NAME, "username").send_keys("testuser123")
        driver.find_element(By.NAME, "password").send_keys("password123")
        
        # Submit using JavaScript
        driver.execute_script("document.querySelector('form').submit()")
        
        # Wait for redirect
        WebDriverWait(driver, 30).until(
            lambda d: "/auth/login" not in d.current_url
        )
        print("✅ Login flow test passed")
        
        print("\n🎉 All Selenium tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
        
    finally:
        try:
            driver.quit()
            print("Chrome WebDriver closed")
        except:
            pass

if __name__ == "__main__":
    flask_process = None
    try:
        # Start Flask server
        flask_process = start_flask_server()
        
        # Run Selenium tests
        success = run_selenium_test()
        
    finally:
        # Clean up: Stop Flask server
        if flask_process:
            print("\nStopping Flask server...")
            try:
                os.kill(flask_process.pid, signal.SIGTERM)
                print("Flask server stopped")
            except:
                flask_process.terminate()
                print("Flask server terminated")
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
