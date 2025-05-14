from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Test parameters
login_url = "http://localhost:5000/login"
share_url_template = "http://localhost:5000/report/{report_id}/share"
username = "existinguser"
password = "ExistingUserPassword"
recipient_username = "recipientuser"
report_id = 1  # the report ID

# Initialize the WebDriver
driver = webdriver.Chrome()

try:
    # Log in as a user who has an analysis report
    driver.get(login_url)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()

    # Wait for the login to complete
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Analyze Text"))
    )

    # Navigate to the report sharing page
    share_url = share_url_template.format(report_id=report_id)
    driver.get(share_url)

    # Enter the username of the user to share the report with
    driver.find_element(By.NAME, "share_with_username").send_keys(recipient_username)
    driver.find_element(By.NAME, "submit").click()

    # Wait for the sharing action to complete and verify success
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Report shared successfully")
    )

    # Log out and log in as the recipient to verify the report is shared
    driver.find_element(By.LINK_TEXT, "Logout").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # Log in as the recipient
    driver.find_element(By.NAME, "username").send_keys(recipient_username)
    driver.find_element(By.NAME, "password").send_keys("RecipientUserPassword1@")  
    driver.find_element(By.NAME, "submit").click()

    # Verify the report appears in the recipient's shared reports list
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Shared Reports")
    )
    assert f"Report {report_id}" in driver.page_source  

except (TimeoutException, NoSuchElementException) as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver
    driver.quit()