from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from datetime import datetime
import time

def job(slot):
    today = datetime.today().day
    driver = Driver(uc=True)  
    driver.keep_alive = True

    # Always start from main tickets page
    driver.get("https://events.humanitix.com/food-hub-2025-semester-2/tickets?c=usulp")

    try:
        # Select date
        date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
        )
        date_button.click()

        # Select time
        time_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{slot}']"))
        )
        time_button.click()

        # Plus button
        plus_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']")
            )
        )
        driver.execute_script("arguments[0].click();", plus_button)

        # Continue
        continue_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']")
            )
        )
        continue_button.click()

        driver.uc_gui_click_captcha()

        # Fill info
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "firstName"))
        ).send_keys("Juntao")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "lastName"))
        ).send_keys("Yu")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        ).send_keys("yujuntao1993@gmail.com")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mobile"))
        ).send_keys("0474836509")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))
        ).click()

        input("Success! Press Enter to exit...")

    except Exception as e:
        print(f"Failed for {slot}, you can check the page.")
        # Browser stays open

# Schedule jobs 2 hours earlier than ticket times
schedule.every().day.at("08:00").do(job, "10:00am")
schedule.every().day.at("09:00").do(job, "11:00am")
schedule.every().day.at("10:00").do(job, "12:00pm")
schedule.every().day.at("11:00").do(job, "1:00pm")
schedule.every().day.at("12:00").do(job, "2:00pm")

while True:
    schedule.run_pending()
    time.sleep(1)
