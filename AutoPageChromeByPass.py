from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from datetime import datetime, timedelta
import time

class TicketTime:
    def __init__(self, time_str, opening_time_str):
        self.time_str = time_str
        self.opening_time_str = opening_time_str

# Define ticket times and their opening times
TICKET_TIMES = [
    TicketTime("10:00am", "08:00"),
    TicketTime("11:00am", "09:00"),
    TicketTime("12:00pm", "10:00"),
    TicketTime("1:00pm", "11:00"),
    TicketTime("2:00pm", "12:00")
]

def attempt_purchase(driver, ticket_time):
    try:
        today = datetime.today().day

        date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
        )
        date_button.click()
        
        time_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{ticket_time}']"))
        )
        time_button.click()

        plus_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']")
            )
        )
        driver.execute_script("arguments[0].click();", plus_button)

        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']")
            )
        )
        continue_button.click()

        driver.uc_gui_click_captcha()

        fill_personal_info(driver)
        return True
    except Exception as e:
        print(f"Failed to purchase ticket for {ticket_time}: {str(e)}")
        return False

def fill_personal_info(driver):
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

    ticket_info_continue = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))
    )
    ticket_info_continue.click()

def job():
    driver = Driver(uc=True)
    driver.keep_alive = True
    
    for ticket in TICKET_TIMES:
        current_time = datetime.now().strftime("%H:%M")
        if current_time >= ticket.opening_time_str:
            print(f"Attempting to purchase ticket for {ticket.time_str}")
            driver.get("https://events.humanitix.com/food-hub-2025-semester-2/tickets?c=usulp")
            
            if attempt_purchase(driver, ticket.time_str):
                print(f"Successfully purchased ticket for {ticket.time_str}")
                input("Press Enter to exit and close browser...")
                return
            
            # Wait 30 seconds before trying the next time slot
            time.sleep(30)
    
    print("Failed to purchase any tickets")
    driver.quit()

# Schedule jobs for each ticket time
for ticket in TICKET_TIMES:
    schedule.every().day.at(ticket.opening_time_str).do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
