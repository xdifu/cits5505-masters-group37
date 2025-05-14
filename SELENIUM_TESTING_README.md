# Selenium Testing for Flask Application

This document provides instructions for running and debugging the Selenium tests in the application.

## Overview

The project has several types of tests:

1. **Unit Tests**: These test individual components in isolation.
2. **Integration Tests**: These test interactions between components.
3. **Selenium Tests**: These are end-to-end tests that simulate user interactions with the application via a browser.

## Prerequisites

- Python 3.10 or higher
- Chrome browser
- ChromeDriver matching your Chrome version

## Installation

1. **Install required packages**:

```bash
pip install -r requirements.txt
```

2. **Install ChromeDriver**:
   - Download ChromeDriver from: https://chromedriver.chromium.org/downloads
   - Make sure the version matches your Chrome browser version
   - Add the ChromeDriver executable to your system PATH

## Running the Flask Application

To run the application locally:

```bash
python run.py
```

The application will be available at http://localhost:5000/

## Running Tests

### Basic Unit Tests

```bash
python -m pytest test/test_models.py test/test_forms.py
```

### Integration Tests

```bash
python -m pytest test/test_auth_routes.py test/test_main_routes.py
```

### Selenium Tests

The Selenium tests are currently experiencing issues with `TimeoutException` errors. These tests require a running Flask server and a working Chrome browser with ChromeDriver.

#### Checking Server Functionality

Use the `verify_server.py` script to check if your Flask server is running properly and can be accessed by Selenium:

```bash
# First, start the Flask server in a separate terminal
python run.py

# In another terminal, run the server verification script
python test/verify_server.py
```

#### Modified Selenium Tests

Due to timing and element detection issues, we've modified the Selenium tests to be more robust. To run them:

```bash
# Run all tests except Selenium tests
python -m pytest -k "not selenium"

# Run only Selenium authentication tests
python -m pytest test/test_selenium.py::TestSeleniumAuth
```

## Debugging Selenium Tests

If you continue to encounter issues with Selenium tests, follow these troubleshooting steps:

1. **Check your Flask application**:
   - Ensure it's running correctly on port 5000
   - Manually verify that the routes being tested work as expected

2. **Modify config.py**:
   - Update `TestingConfig` to use a file-based SQLite database
   - Disable CSRF protection during testing

3. **Run with verbose output and debug logs**:
   - Use the `-v` flag for verbose output
   - Check the log file for detailed information on test execution

4. **Visual Debugging**:
   - Remove the `--headless` option to see the browser in action
   - Add screenshots at key points in the test

## Known Issues and Solutions

1. **TimeoutException** - Elements not found within the timeout period
   - Solution: Increase wait times, use more specific selectors, verify element presence in the HTML

2. **Database Inconsistency** - Tests not seeing database changes
   - Solution: Use a file-based SQLite database instead of in-memory database

3. **Element Click Intercepted** - Elements can't be clicked
   - Solution: Use JavaScript to click elements or submit forms, scroll elements into view before clicking

## Next Steps

After the basic auth tests are passing, the more complex tests for analysis and dashboard features can be enabled. These have been skipped for now while focusing on the fundamental authentication tests.

## Files

- `test_selenium.py` - The main Selenium test file (currently having issues)
- `test_selenium_simple.py` - A simplified version of the Selenium tests
- `verify_server.py` - A standalone script to verify server functionality with Selenium
- `SELENIUM_TESTING_GUIDE.md` - Comprehensive guide to Selenium testing in this application
