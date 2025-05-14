# Standalone Selenium test for Flask application
# This file is intended to be run separately after the Flask app is already running
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_test():
    """Run simple Selenium tests against a running Flask server."""
    print("Starting Selenium test...")
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Test 1: Check if the homepage loads
        print("Testing homepage...")
        driver.get("http://localhost:5000/")
        assert "Welcome" in driver.title or "Welcome" in driver.page_source
        print("✅ Homepage loaded successfully")
        
        # Test 2: Check if login page loads
        print("Testing login page...")
        driver.get("http://localhost:5000/auth/login")
        assert "Login" in driver.title or "Login" in driver.page_source
        print("✅ Login page loaded successfully")
        
        # Test 3: Check if register page loads
        print("Testing registration page...")
        driver.get("http://localhost:5000/auth/register")
        assert "Register" in driver.title or "Register" in driver.page_source
        print("✅ Registration page loaded successfully")
        
        # Show success message
        print("\n🎉 All tests passed! The Flask server is running properly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"Current URL: {driver.current_url}")
        print("Page source snippet:")
        print(driver.page_source[:500] + "...")
        return False
    finally:
        # Clean up
        driver.quit()
    
    return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
