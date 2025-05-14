import unittest
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestRegistrationFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up Chrome driver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Optional: headless mode
        service = Service()
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    def test_register_user(self):
        driver = self.driver
        driver.get(f"{self.base_url}/auth/register")

        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        # Generate a random, valid user
        random_username = f"selenium_{uuid.uuid4().hex[:6]}"
        random_email = f"{random_username}@example.com"
        secure_password = "Test1234!"  # ✅ Valid format: uppercase, lowercase, number, special char

        # Fill in the form
        driver.find_element(By.ID, "username").send_keys(random_username)
        driver.find_element(By.NAME, "username").send_keys(random_username)
        driver.find_element(By.NAME, "email").send_keys(random_email)
        driver.find_element(By.NAME, "password").send_keys(secure_password)
        driver.find_element(By.NAME, "password2").send_keys(secure_password)

        # Submit the form
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(1)

        # Confirm redirection to login page
        self.assertIn("login", driver.current_url.lower())

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()