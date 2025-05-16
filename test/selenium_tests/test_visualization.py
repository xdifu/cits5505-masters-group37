"""
This Selenium test case is designed to verify the visualization page of a Flask-based web application.

Summary of Logic:
1. The `setUpClass` method configures the Chrome WebDriver to run in headless mode and performs user login using the "test1" account.
2. The `test_visualization_elements` method navigates to the /visualization page and waits for the page to load.
   - It checks if the header text "Sentiment Analytics Dashboard" is present.
   - It verifies that the three expected charts (barChart, pieChart, and lineChart) are present and visible on the page.
3. The `tearDownClass` method cleanly shuts down the WebDriver after tests complete.

Purpose:
Ensure that the visualization page is correctly rendered, all major chart elements are loaded, and the user is authenticated beforehand.
"""
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestVisualizationPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service()
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

        # Login first
        cls.driver.get(f"{cls.base_url}/auth/login")
        cls.driver.find_element(By.NAME, "username").send_keys("test1")
        cls.driver.find_element(By.NAME, "password").send_keys("Test1234!")
        cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(cls.driver, 5).until(
            EC.url_contains("/index")
        )

    def test_visualization_elements(self):
        driver = self.driver
        driver.get(f"{self.base_url}/visualization")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertIn("Sentiment Analytics Dashboard", driver.page_source)

        bar = driver.find_element(By.ID, "barChart")
        pie = driver.find_element(By.ID, "pieChart")
        line = driver.find_element(By.ID, "lineChart")

        self.assertTrue(bar.is_displayed())
        self.assertTrue(pie.is_displayed())
        self.assertTrue(line.is_displayed())

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()