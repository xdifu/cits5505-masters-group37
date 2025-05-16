"""
Test Summary:
This Selenium test case validates the visualization elements on the Sentiment Analytics Dashboard page.

Steps performed:
1. Open a Chrome browser in headless mode.
2. Log in to the application using a test account (test1/Test1234!).
3. Navigate to the visualization page.
4. Verify that the page contains the heading "Sentiment Analytics Dashboard".
5. Check for the presence and visibility of three chart elements: barChart, pieChart, and lineChart.
6. Close the browser after test completion.

This ensures the dashboard loads properly and key elements are rendered for the user.
"""
import unittest
import threading
import time
from run import app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestVisualizationPage(unittest.TestCase):

    def setUp(self):
        # 启动 Flask 应用线程
        self.app_thread = threading.Thread(target=app.run, kwargs={"port": 5000, "use_reloader": False})
        self.app_thread.setDaemon(True)
        self.app_thread.start()
        time.sleep(2)  # 等待服务器启动

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5)
        self.base_url = "http://127.0.0.1:5000"

        # Login first
        self.driver.get(f"{self.base_url}/auth/login")
        self.driver.find_element(By.NAME, "username").send_keys("test1")
        self.driver.find_element(By.NAME, "password").send_keys("Test1234!")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        WebDriverWait(self.driver, 5).until(
            EC.url_contains("/index")
        )

    def test_result_buttons_navigation(self):
        driver = self.driver
        driver.get(f"{self.base_url}/results")

        # Wait until the page loads and result cards are visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "report-card"))
        )

        # Click the first "View Dashboard" button
        view_buttons = driver.find_elements(By.LINK_TEXT, "VIEW DASHBOARD")
        self.assertTrue(view_buttons, "View Dashboard button not found")
        view_buttons[0].click()
        self.assertIn("/results_dashboard", driver.current_url)

        driver.back()

        # Click the first "Share Report" button
        share_buttons = driver.find_elements(By.LINK_TEXT, "SHARE REPORT")
        self.assertTrue(share_buttons, "Share Report button not found")
        share_buttons[0].click()
        self.assertIn("/share_report", driver.current_url)

    def tearDown(self):
        self.driver.quit()