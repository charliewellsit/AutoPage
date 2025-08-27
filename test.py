from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()  # Selenium handles driver management
driver.get("https://events.humanitix.com/food-hub-2025-semester-2/tickets?c=usulp")

# Wait until the plus button is enabled (data-disabled="false")
plus_button = WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']")
    )
)
plus_button.click()

# testing