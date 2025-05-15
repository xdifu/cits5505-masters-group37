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

        # Analyze text
        driver.get(f"{self.base_url}/analyze")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "news_text")))
        driver.find_element(By.ID, "news_text").send_keys("This is a test article for sharing.")
        driver.find_element(By.ID, "submit").click()
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

        # Check shared_with_me
        driver.get(f"{self.base_url}/shared_with_me")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "shared-report-card")))
        self.assertIn("test article", driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()