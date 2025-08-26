from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from datetime import datetime
import time
import threading

tickets = [
    {
        "email": "yujuntao1993@gmail.com",
        "first_name": "Juntao",
        "last_name": "Yu",
        "phone": "0474836509"
    },
    {
        "email": "friend@example.com",
        "first_name": "FriendFirstName",
        "last_name": "FriendLastName",
        "phone": "0498765432"
    }
]

url = "https://events.humanitix.com/food-hub-2025-semester-2/tickets?c=usulp"

def book_ticket(ticket):
    today = datetime.today().day

    # run in background without GUI
    options = Options()
    # options.add_argument("--headless")  
    # options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("detach", True)  # Keep browser open

    driver = webdriver.Chrome(options=options)
    driver.get(url)  # same URL for both tickets

    # Select date
    date_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
    )
    date_button.click()

    # Select time
    time_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='10:00am']"))
    )
    time_button.click()

    # Click plus button
    plus_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "plus"))
    )
    plus_button.click()

    # Continue
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='checkout-btn']"))
    )
    continue_button.click()

    # Fill personal info
    email_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_box.send_keys(ticket["email"])
    driver.find_element(By.NAME, "phone").send_keys(ticket["phone"])
    driver.find_element(By.NAME, "firstName").send_keys(ticket["first_name"])
    driver.find_element(By.NAME, "lastName").send_keys(ticket["last_name"])

    print(f"{ticket['first_name']} info filled at {datetime.now()}")
    time.sleep(5)
    driver.quit()

def job():
    threads = []
    for ticket in tickets:
        t = threading.Thread(target=book_ticket, args=(ticket,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

schedule.every().day.at("8:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)


