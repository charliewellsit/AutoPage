from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, time as dtime
import schedule
import time

class TicketTime:
    def __init__(self, ticket_str, opening_str):
        self.ticket_str = ticket_str
        self.opening_str = opening_str
        self.opening_time = datetime.strptime(opening_str, "%H:%M").time()

# Define ticket times and their opening times
TICKET_TIMES = [
    TicketTime("10:00am", "08:00"),
    TicketTime("11:00am", "09:00"),
    TicketTime("12:00pm", "10:00"),
    TicketTime("1:00pm", "11:00"),
    TicketTime("2:00pm", "12:00")
]

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

def attempt_purchase(ticket_time_str):
    driver.get("https://events.humanitix.com/food-hub-2025-semester-2/tickets?c=usulp")
    today = datetime.today().day

    try:
        # Select today's date
        date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
        )
        date_button.click()

        # Select ticket time
        time_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{ticket_time_str}']"))
        )
        time_button.click()

        # Click plus button
        plus_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']"))
        )
        driver.execute_script("arguments[0].click();", plus_button)

        # Click continue button
        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']"))
        )
        continue_button.click()

        # Handle CAPTCHA if present
        driver.uc_gui_click_captcha()

        # Fill personal info
        fill_personal_info(driver)
        return True

    except Exception as e:
        print(f"Failed to purchase ticket for {ticket_time_str}: {e}")
        return False

def job():
    print("Checking ticket availability...")
    now = datetime.now().time()

    for ticket in TICKET_TIMES:
        # Skip tickets that haven't opened yet
        if now < ticket.opening_time:
            continue

        print(f"Attempting ticket for {ticket.ticket_str}")
        success = attempt_purchase(ticket.ticket_str)
        if success:
            print(f"Successfully purchased ticket for {ticket.ticket_str}")
            # Keep the browser open; just stop script logic
            return

    print("No tickets purchased this round. Waiting for next scheduled run.")

# Initialize driver once and keep open
driver = Driver(uc=True)
driver.keep_alive = True

# Schedule jobs for all opening times
for ticket in TICKET_TIMES:
    schedule.every().day.at(ticket.opening_str).do(job)

print("Ticket automation script running...")
while True:
    schedule.run_pending()
    time.sleep(1)
