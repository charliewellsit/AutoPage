from selenium import webdriver
from selenium.webdriver.Edge.options import Options
from selenium.webdriver.common.by import By
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
    # options.add_argument("--headless")  
    # options.add_argument("--window-size=1920,1080")
    # driver = webdriver.Edge(options=options) 
    options.add_experimental_option("detach", True)  # Keep browser open

    driver = webdriver.Edge(options=options)  # Selenium handles driver management
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

    # Now click the plus button
    plus_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "plus"))
    )
    plus_button.click()

    # Click the continue button
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='checkout-btn']"))
    )
    continue_button.click()

    # Fill email
    email_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_box.send_keys("yujuntao1993@gmail.com")

    # Fill phone
    phone_box = driver.find_element(By.NAME, "phone")
    phone_box.send_keys("0474836509")

    # Fill first name
    first_name_box = driver.find_element(By.NAME, "firstName")
    first_name_box.send_keys("Juntao")

    # Fill last name
    last_name_box = driver.find_element(By.NAME, "lastName")
    last_name_box.send_keys("Yu")

# Schedule job
schedule.every().day.at("8:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

