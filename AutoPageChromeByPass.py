from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from datetime import datetime
import time

# =========================
# --- User Configurable ---
# =========================
First_Name = "Juntao"
Last_Name = "Yu"
Email = "yujuntao1993@gmail.com"
Mobile = "0474836509"

Domestic_or_International = "International"  # Options: "Domestic" or "International"
Postgrad_or_Undergrad = "Postgraduate"       # Options: "Postgraduate" or "Undergraduate"

# =========================
# --- Booking Function ---
# =========================
def job(slot):
    today = datetime.today().day
    driver = Driver(uc=True)  
    driver.keep_alive = True

    # Always start from main tickets page
    driver.get("https://events.humanitix.com/food-hub-2026-semester-1/tickets?c=app")

    try:
        # --- Select date ---
        date_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
        )
        date_button.click()

        # --- Select time ---
        time_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{slot}']"))
        )
        time_button.click()

        # --- Plus button ---
        plus_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']")
            )
        )
        driver.execute_script("arguments[0].click();", plus_button)

        # --- Continue ---
        continue_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']")
            )
        )
        driver.execute_script("arguments[0].click();", continue_button)

        driver.uc_gui_click_captcha()

        # --- Fill info ---
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "firstName"))
        ).send_keys(First_Name)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "lastName"))
        ).send_keys(Last_Name)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "email"))
        ).send_keys(Email)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "mobile"))
        ).send_keys(Mobile)

        # Wait for Cloudflare check
        time.sleep(2)

        WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))
        ).click()

        # --- Select Domestic/International ---
        dropdown1 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label/span[contains(text(),'domestic or international')]/ancestor::div[contains(@class,'Select')]//div[@role='combobox']")
            )
        )
        dropdown1.click()

        option1 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[@role='option' and normalize-space()='{Domestic_or_International}']")
            )
        )
        option1.click()

        # --- Select Postgraduate/Undergraduate ---
        dropdown2 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label/span[contains(text(),'postgraduate or undergraduate')]/ancestor::div[contains(@class,'Select')]//div[@role='combobox']")
            )
        )
        dropdown2.click()

        option2 = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[@role='option' and normalize-space()='{Postgrad_or_Undergrad}']")
            )
        )
        option2.click()

        continue_btn = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='ticket-info-submit']"))
        )
        continue_btn.click()

        # --- SUCCESS CHECK ---
        try:
            WebDriverWait(driver, 60).until(
                EC.any_of(
                    EC.url_contains("complete"),
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'View ticket')]"))
                )
            )
            print(f"Booking for {slot} succeeded! Closing browser and stopping scheduler.")
            driver.quit()
            schedule.clear()   # stop all jobs
            return
        except:
            print(f"Booking flow for {slot} did not reach success page, will keep scheduler running...")

    except Exception as e:
        print(f"Failed for {slot}, you can check the page.")
        # Browser stays open

# =========================
# --- Scheduler ---
# =========================
schedule.every().day.at("08:00").do(job, "10:00am")
schedule.every().day.at("08:30").do(job, "10:30am") 
schedule.every().day.at("09:00").do(job, "11:00am")
schedule.every().day.at("09:30").do(job, "11:30am")  
schedule.every().day.at("10:00").do(job, "12:00pm")
schedule.every().day.at("10:30").do(job, "12:30pm")  
schedule.every().day.at("11:00").do(job, "1:00pm")
schedule.every().day.at("11:30").do(job, "1:30pm")   
schedule.every().day.at("12:00").do(job, "2:00pm")

while True:
    schedule.run_pending()
    time.sleep(1)
