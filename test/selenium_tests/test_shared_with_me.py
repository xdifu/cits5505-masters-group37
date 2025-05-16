import unittest
import random
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestSharedWithMeFlow(unittest.TestCase):
    """End-to-end test for sharing a report and viewing it under 'Shared With Me'."""

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        # 在调试时保持可见，修复后可以重新启用无头模式
        #chrome_options.add_argument("--headless")
        service = Service()
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    def test_shared_with_me_workflow(self):
        driver = self.driver

        # 1. Log in as user 'test1'
        driver.get(f"{self.base_url}/auth/login")
        driver.find_element(By.NAME, "username").send_keys("test3")
        driver.find_element(By.NAME, "password").send_keys("Test1234!")
        login_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
        driver.execute_script("arguments[0].click();", login_btn)
        
        # 打印当前URL，帮助调试
        print(f"After login, URL: {driver.current_url}")
        
        # 2. 导航到分析页面并找正确的输入框
        driver.get(f"{self.base_url}/analyze")
        
        # 短暂延迟以便页面完全加载
        time.sleep(1)
        
        # 尝试查找页面中所有可能的文本输入元素
        text_areas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"Found {len(text_areas)} textareas on the page")
        
        # 查看第一个文本区域的ID
        if text_areas:
            print(f"First textarea ID: {text_areas[0].get_attribute('id')}")
            textarea_id = text_areas[0].get_attribute('id')
        else:
            # 如果没有找到textarea，尝试其他选择器
            textarea_id = "analysis-text"  # 假设的ID
        
        # 使用找到的或假设的ID
        shared_text = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=25))
        
        # 先等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "textarea"))
        )
        
        # 找到文本区域并输入文本
        driver.find_element(By.TAG_NAME, "textarea").send_keys(shared_text)
        
        # 找到并点击提交按钮
        submit_btn = driver.find_element(By.ID, "submit")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        driver.execute_script("arguments[0].click();", submit_btn)

        # 3. Wait for navigation to results page, then grab the timestamp
        WebDriverWait(driver, 10).until(EC.url_contains("/results"))
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "report-card-timestamp"))
        )
        timestamp_text = driver.find_element(By.CLASS_NAME, "report-card-timestamp").text

        # 4. Click 'Share Report' for the first report card
        share_buttons = driver.find_elements(By.LINK_TEXT, "Share Report")
        share_buttons[0].click()
        WebDriverWait(driver, 5).until(EC.url_contains("/share_report"))

        # 5. Quick-share to user 'test2'
        driver.find_element(By.ID, "user_search").send_keys("test2")
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.NAME, "share_user")))
        driver.find_element(By.NAME, "share_user").click()
        # click the share button to submit
        share_submit = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        share_submit.click()

        # 6. Logout test1
        driver.get(f"{self.base_url}/auth/logout")

        # 7. Log in as user 'test2'
        driver.get(f"{self.base_url}/auth/login")
        driver.find_element(By.NAME, "username").send_keys("test2")
        driver.find_element(By.NAME, "password").send_keys("Test1234!")
        login_btn2 = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", login_btn2)
        driver.execute_script("arguments[0].click();", login_btn2)

        # 8. Visit 'Shared With Me' and verify the shared report appears
        driver.get(f"{self.base_url}/shared_with_me")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "shared-report-card"))
        )
        self.assertIn(timestamp_text, driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()