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

        # Login as test1
        driver.get(f"{self.base_url}/auth/login")
        driver.find_element(By.NAME, "username").send_keys("test1")
        driver.find_element(By.NAME, "password").send_keys("Test1234!")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/index"))

        # Generate random article text over 10 characters
        shared_text = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=25))

        # Analyze text
        driver.get(f"{self.base_url}/analyze")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "news_text")))
        driver.find_element(By.ID, "news_text").send_keys(shared_text)
        driver.find_element(By.ID, "submit").click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "report-card-timestamp")))
        timestamp_text = driver.find_element(By.CLASS_NAME, "report-card-timestamp").text
        WebDriverWait(driver, 10).until(EC.url_contains("/results"))

        # Share the report
        share_buttons = driver.find_elements(By.LINK_TEXT, "Share Report")
        share_buttons[0].click()
        WebDriverWait(driver, 5).until(EC.url_contains("/share_report"))
        driver.find_element(By.ID, "user_search").send_keys("test2")
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.NAME, "share_user")))
        driver.find_element(By.NAME, "share_user").click()

        # Logout
        driver.get(f"{self.base_url}/auth/logout")

        # Login as test2
        driver.get(f"{self.base_url}/auth/login")
        driver.find_element(By.NAME, "username").send_keys("test2")
        driver.find_element(By.NAME, "password").send_keys("Test1234!")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/index"))

        # Visit shared_with_me as test2 and verify timestamp matches
        driver.get(f"{self.base_url}/shared_with_me")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "shared-report-card")))
        self.assertIn(timestamp_text, driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()