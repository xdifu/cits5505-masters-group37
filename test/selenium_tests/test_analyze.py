"""
Selenium Test: Analyze Flow

This test simulates a user logging into the application and submitting text to be analyzed.
The steps covered in this test are:
1. Set up the Chrome driver in headless mode and navigate to the login page.
2. Log in with test credentials ("test1" / "Test1234!") and confirm successful navigation to the index page.
3. Navigate to the Analyze page and wait for the text input field to be ready.
4. Enter a sample news text and submit it for analysis.
5. Wait for the results page to render, verifying that "Keywords" and "Sentiment" are present in the output.

The test ensures that:
- The login works with valid credentials.
- The Analyze form is accessible and functional.
- The backend processes input text and returns expected analysis results.
"""
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------------- Analyze Flow Selenium Test ----------------------
class TestAnalyzeFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service()
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

        # Perform login
        cls.driver.get(f"{cls.base_url}/auth/login")
        cls.driver.find_element(By.NAME, "username").send_keys("test1")
        cls.driver.find_element(By.NAME, "password").send_keys("Test1234!")
        cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(cls.driver, 10).until(
            EC.url_contains("/index")
        )

    def test_analyze_text_submission(self):
        driver = self.driver
        driver.get(f"{self.base_url}/index")
        driver.get(f"{self.base_url}/analyze")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "news_text"))
        )
        driver.find_element(By.NAME, "news_text").send_keys("This is a test input provided for the purpose of conducting analysis and drawing insights.")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Keywords')]"))
        )
        self.assertIn("Sentiment", driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()