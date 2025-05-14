# Enhanced server verification script with more detailed error handling
import sys
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

def check_server_without_selenium():
    """Check if the server is running without using Selenium"""
    import requests
    print("\n--- Checking server with basic HTTP request ---")
    try:
        response = requests.get("http://localhost:5000/")
        print(f"Server responded with status code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is running and responding to requests")
            return True
        else:
            print(f"❌ Server responded with non-200 status: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Could not connect to server at http://localhost:5000/")
        print("   Make sure your Flask application is running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def test_with_selenium():
    """Test the server using Selenium with enhanced error handling"""
    print("\n--- Starting Selenium test with enhanced error reporting ---")
    driver = None
    
    try:
        # Try to initialize Chrome driver
        print("Setting up Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ Chrome WebDriver initialized successfully")
        except WebDriverException as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("\nPossible solutions:")
            print("1. Make sure Chrome is installed")
            print("2. Make sure ChromeDriver is installed and in your PATH")
            print("3. Try installing the latest ChromeDriver from: https://chromedriver.chromium.org/downloads")
            return False
            
        driver.implicitly_wait(10)
        driver.maximize_window()
        
        # Test 1: Homepage
        print("\nTesting homepage...")
        try:
            driver.get("http://localhost:5000/")
            print(f"✓ Loaded URL: {driver.current_url}")
        except Exception as e:
            print(f"❌ Failed to load homepage: {e}")
            return False
            
        print(f"Page title: '{driver.title}'")
        
        # Check for expected content in a more flexible way
        if "Welcome" in driver.title or "Welcome" in driver.page_source:
            print("✅ Homepage contains 'Welcome' text")
        else:
            print("❌ Homepage does not contain expected 'Welcome' text")
            print("First 1000 characters of page source:")
            print(driver.page_source[:1000] + "...")
            return False
            
        # Test 2: Login page
        print("\nTesting login page...")
        try:
            driver.get("http://localhost:5000/auth/login")
            print(f"✓ Loaded URL: {driver.current_url}")
        except Exception as e:
            print(f"❌ Failed to load login page: {e}")
            return False
            
        print(f"Page title: '{driver.title}'")
        
        if "Login" in driver.title or "Login" in driver.page_source:
            print("✅ Login page contains 'Login' text")
        else:
            print("❌ Login page does not contain expected 'Login' text")
            print("First 1000 characters of page source:")
            print(driver.page_source[:1000] + "...")
            return False
            
        # Test 3: Register page
        print("\nTesting registration page...")
        try:
            driver.get("http://localhost:5000/auth/register")
            print(f"✓ Loaded URL: {driver.current_url}")
        except Exception as e:
            print(f"❌ Failed to load registration page: {e}")
            return False
            
        print(f"Page title: '{driver.title}'")
        
        if "Register" in driver.title or "Register" in driver.page_source:
            print("✅ Registration page contains 'Register' text")
        else:
            print("❌ Registration page does not contain expected 'Register' text")
            print("First 1000 characters of page source:")
            print(driver.page_source[:1000] + "...")
            return False
            
        # All tests passed!
        print("\n🎉 All Selenium tests passed! The Flask server is running properly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error during tests: {e}")
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            print("\nClosing WebDriver...")
            driver.quit()

if __name__ == "__main__":
    print("=== Flask Server Verification Tool ===")
    
    # First check with simple HTTP request
    if not check_server_without_selenium():
        print("\nServer check failed. Please make sure your Flask application is running with:")
        print("python run.py")
        sys.exit(1)
        
    # Then check with Selenium
    if test_with_selenium():
        print("\nAll tests passed! Your server is properly configured for Selenium tests.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please review the error messages above.")
        sys.exit(1)
