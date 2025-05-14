import unittest
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
        service = Service()  # 自动找 chromedriver
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    def test_register_user(self):
        driver = self.driver
        driver.get(f"{self.base_url}/auth/register")

        print("🟡 Current URL:", driver.current_url)
        print("🟡 Page snippet ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓")
        print(driver.page_source[:1000])  # 打印前 1000 字符页面内容
        print("🟡 ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑")

        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "username"))
)
        driver.find_element(By.ID, "username").send_keys("selenium_user")

        # Enter username, email, and password (modify according to actual HTML name or id)
        driver.find_element(By.NAME, "username").send_keys("selenium_user")
        driver.find_element(By.NAME, "email").send_keys("selenium@example.com")
        driver.find_element(By.NAME, "password").send_keys("testpassword")
        driver.find_element(By.NAME, "password2").send_keys("testpassword")

        # Submit the form
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(1)

        # Check whether the page redirected or showed success message
        self.assertIn("login", driver.current_url.lower())  # 例：注册成功后跳转到 login 页面

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()


# ---------------------- Analyze Flow Selenium Test ----------------------
class TestAnalyzeFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service()
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://localhost:5000"

    def test_analyze_text_submission(self):
        driver = self.driver
        driver.get(f"{self.base_url}/analyze")

        print("🟡 Navigated to:", driver.current_url)
        print(driver.page_source[:1000])

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "input_text"))
        )
        driver.find_element(By.NAME, "input_text").send_keys("This is a test input for analysis.")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.url_contains("/results_dashboard")
        )
        self.assertIn("/results_dashboard", driver.current_url)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()