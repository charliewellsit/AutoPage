from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

today = datetime.today().day

# Use SeleniumBase with undetected-chromedriver
driver = Driver(uc=True)  
driver.keep_alive = True  # Keep browser open

driver.get("https://events.humanitix.com/food-hub-2025-semester-2/tickets?c=usulp")

# Wait until the button with today’s number appears and click it
date_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
)
date_button.click()

# Wait until the time button "2:00pm" appears and click it
time_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='10:00am']"))
)
time_button.click()

# Wait until the plus button is enabled and click
plus_button = WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']")
    )
)
plus_button.click()

# More reliable plus button click using JavaScript
plus_button = WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']")
    )
)
driver.execute_script("arguments[0].click();", plus_button)

# 🔐 Handle Cloudflare challenge right here
driver.uc_gui_click_captcha()

# ==== Fill in your info ====
first_name_input = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "firstName"))
)
first_name_input.send_keys("Juntao")

last_name_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "lastName"))
)
last_name_input.send_keys("Yu")

email_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "email"))
)
email_input.send_keys("yujuntao1993@gmail.com")

mobile_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "mobile"))
)
mobile_input.send_keys("0474836509")

# Continue to Ticket Info
ticket_info_continue = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))
)
ticket_info_continue.click()

# Keep browser open until user input
input("Press Enter to exit and close browser...")