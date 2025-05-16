"""
This test automates the full 'Shared With Me' feature flow in the web application.

Test Summary:
- Logs in as user test1.
- Submits a dummy analysis request on the /analyze page with a fixed test string.
- Captures the resulting timestamp from the generated report on the /results page.
- Clicks the "Share Report" button to go to /share_report and shares the report with user test2.
- Logs out as test1 and logs in as test2.
- Visits the /shared_with_me page as test2 to verify that the shared report appears.
- Validates that the timestamp (date and time) from the original submission appears on test2’s shared report page.

Assumptions:
- The application is running at http://127.0.0.1:5000.
- Users test1 and test2 already exist with password "Test1234!".
- Each report has a "Share Report" link that navigates to a share form with an input field id='share_with_username' and a submit button with id='submit'.
- Shared reports appear on the /shared_with_me page with class "list-group-item" and their timestamp format matches "%Y-%m-%d %H:%M UTC".
"""
import unittest
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Shared With Me Flow Test ---
class TestSharedWithMeFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service()
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    def test_shared_with_me_workflow(self):
        driver = self.driver

        # Step 1: Login as test1
        driver.get(f"{self.base_url}/auth/login")
        driver.find_element(By.NAME, "username").send_keys("test1")
        driver.find_element(By.NAME, "password").send_keys("Test1234!")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/index"))

        # Step 2: Go to /analyze and submit random text
        driver.get(f"{self.base_url}/analyze")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "news_text")))
        shared_text = "This is an automated test input with more than ten words to ensure uniqueness and visibility."
        driver.find_element(By.ID, "news_text").send_keys(shared_text)
        driver.find_element(By.ID, "submit").click()
        driver.get(f"{self.base_url}/results")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "report-card-timestamp")))

        # Step 3: On /results, capture timestamp of first card
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "report-card-timestamp")))
        timestamp_text = driver.find_element(By.CLASS_NAME, "report-card-timestamp").text

        # Step 4: Click first "Share Report" button
        print("URL:", driver.current_url)
        print("HTML snippet:", driver.page_source[:1000])

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Share Report')]"))
            )
            share_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Share Report')]")
            print("Found Share Buttons:", len(share_buttons))
            share_buttons[0].click()
            WebDriverWait(driver, 10).until(EC.url_contains("/share_report"))
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "share_with_username"))).send_keys("test2")
            driver.find_element(By.ID, "submit").click()
        except Exception as e:
            print("Failed to find or click Share Report button:", e)
            self.fail("Share Report button not found or failed to click")

        # Step 5: Logout as test1
        driver.get(f"{self.base_url}/auth/logout")

        # Step 6: Login as test2
        driver.get(f"{self.base_url}/auth/login")
        driver.find_element(By.NAME, "username").send_keys("test2")
        driver.find_element(By.NAME, "password").send_keys("Test1234!")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/index"))

        # Step 7: Visit /shared_with_me and validate timestamp
        driver.get(f"{self.base_url}/shared_with_me")
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "list-group-item")))
        except Exception:
            self.fail("No shared report card (list-group-item) found on shared_with_me page.")
        from datetime import datetime
        raw_time = timestamp_text.replace("UTC", "").strip()
        base_time = datetime.strptime(raw_time, "%Y-%m-%d %H:%M")
        formatted_date = base_time.strftime("%Y-%m-%d")
        formatted_time = base_time.strftime("%H:%M")
        self.assertTrue(formatted_date in driver.page_source and formatted_time in driver.page_source,
                        f"Expected date {formatted_date} and time {formatted_time} not found in shared page.")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()