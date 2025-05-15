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