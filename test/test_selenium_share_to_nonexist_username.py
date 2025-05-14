from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Test parameters
login_url = "http://localhost:5000/login"
share_url_template = "http://localhost:5000/report/{report_id}/share"
username = "existinguser"
password = "ExistingUserPassword"
non_existent_username = "nonexistentuser"
report_id = 1  

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

    # Enter a non-existent username to share the report with
    driver.find_element(By.NAME, "share_with_username").send_keys(non_existent_username)
    driver.find_element(By.NAME, "submit").click()

    # Wait for the error message to appear
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "User not found. Please enter a valid username.")
    )

    # Verify the error message is displayed
    assert "User not found. Please enter a valid username." in driver.page_source

except (TimeoutException, NoSuchElementException) as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver
    driver.quit()