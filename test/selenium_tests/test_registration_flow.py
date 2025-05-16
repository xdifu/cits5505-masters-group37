"""
This Selenium test suite verifies the registration functionality of the web application.

Test Overview:
--------------
- The test navigates to the user registration page (/auth/register).
- It waits for the registration form to load by checking for the presence of the username input field.
- A random username is generated using UUID to avoid duplicates during testing.
- A secure password is defined that meets common validation rules (uppercase, lowercase, number, special character).
- The test fills out the registration form with:
    * Random username (for both ID and name fields)
    * Random email
    * Password and confirmation
- It then submits the form by clicking the submit button.
- After submission, the test checks that the page redirects to the login page,
  confirming that registration was successful.

"""
import unittest
import uuid
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from run import app  # 确保 run.py 中有 app 实例

class TestRegistrationFlow(unittest.TestCase):

    def setUp(self):
        # 启动 Flask 应用线程
        self.app_thread = threading.Thread(target=app.run, kwargs={"port": 5000, "use_reloader": False})
        self.app_thread.setDaemon(True)
        self.app_thread.start()
        time.sleep(1)  # 等待服务器启动

        # 初始化浏览器
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5)
        self.base_url = "http://127.0.0.1:5000"

    def test_register_user(self):
        driver = self.driver
        driver.get(f"{self.base_url}/auth/register")

        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        random_username = f"selenium_{uuid.uuid4().hex[:6]}"
        random_email = f"{random_username}@example.com"
        secure_password = "Test1234!"  # ✅ Valid format

        driver.find_element(By.ID, "username").send_keys(random_username)
        driver.find_element(By.NAME, "username").send_keys(random_username)
        driver.find_element(By.NAME, "email").send_keys(random_email)
        driver.find_element(By.NAME, "password").send_keys(secure_password)
        driver.find_element(By.NAME, "password2").send_keys(secure_password)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(1)
        self.assertIn("login", driver.current_url.lower())

    def tearDown(self):
        self.driver.quit()