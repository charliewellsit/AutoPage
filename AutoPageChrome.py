from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from datetime import datetime
import time

def job():
    # Get today’s date (day number only)
    today = datetime.today().day

    # run in background without GUI
    options = Options()
    options.add_experimental_option("detach", True)  # Keep browser open

    driver = webdriver.Chrome(options=options)  # Selenium handles driver management
    driver.get("https://events.humanitix.com/food-hub-2025-semester-2/tickets?c=usulp")

    # Wait until the button with today’s number appears and click it
    date_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
    )
    date_button.click()
    
    # Wait until the time button "10:00am" appears and click it
    time_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='10:00am']"))
    )
    time_button.click()

    # Wait until the plus button is enabled (data-disabled="false")
    plus_button = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']"))
    )
    driver.execute_script("arguments[0].click();", plus_button)

    # Wait until the continue button is enabled
    continue_button = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']"))
    )
    continue_button.click()

    # Wait until the First Name input is present, then fill it
    first_name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "firstName"))
    )
    first_name_input.send_keys("Juntao")

    # Last Name
    last_name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "lastName"))
    )
    last_name_input.send_keys("Yu")

    # Email
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_input.send_keys("yujuntao1993@gmail.com")

    # Mobile
    mobile_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mobile"))
    )
    mobile_input.send_keys("0474836509")

    # Wait until the "Continue to Ticket Info" button is clickable, then click it
    ticket_info_continue = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))
    )
    ticket_info_continue.click()

# Schedule job
schedule.every().day.at("08:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

