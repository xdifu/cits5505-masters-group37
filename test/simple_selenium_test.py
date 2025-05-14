"""
Simple standalone test script that doesn't require pytest
This should run more easily in the VS Code terminal
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def run_simple_test():
    """Simple test to check if we can use Selenium with Chrome"""
    print("\n=== Starting Simple Selenium Test ===")
    
    # Try to create a Chrome driver instance
    try:
        print("Initializing Chrome driver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        print("✓ Chrome driver initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Chrome driver: {e}")
        print("\nPossible solutions:")
        print("1. Make sure Chrome is installed")
        print("2. Make sure ChromeDriver is installed and compatible with your Chrome version")
        print("3. Download ChromeDriver from: https://chromedriver.chromium.org/downloads")
        return False
    
    try:
        # Test navigation to a simple site
        print("\nTesting navigation to Google...")
        driver.get("https://www.google.com")
        time.sleep(2)  # Wait for page to load
        print(f"✓ Successfully loaded: {driver.current_url}")
        print(f"✓ Page title: {driver.title}")
        
        if "Google" in driver.title:
            print("✓ Page title contains 'Google'")
        else:
            print("✗ Page title does NOT contain 'Google'")
            
        # Now try to navigate to localhost if server is running
        print("\nTrying to connect to local Flask server...")
        try:
            driver.get("http://localhost:5000")
            time.sleep(2)
            print(f"✓ Successfully loaded localhost: {driver.current_url}")
            print(f"✓ Page title: {driver.title}")
            print("✓ Flask server appears to be running")
        except Exception as e:
            print(f"✗ Could not connect to Flask server: {e}")
            print("  Make sure your Flask app is running on port 5000")
            
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        try:
            driver.quit()
            print("\nChrome driver closed successfully")
        except:
            pass

if __name__ == "__main__":
    success = run_simple_test()
    sys.exit(0 if success else 1)
