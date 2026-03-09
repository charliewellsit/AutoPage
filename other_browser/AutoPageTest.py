from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule # 虽然测试版不用，但保留以维持结构一致
from datetime import datetime
import time

# =========================
# --- User Configurable ---
# =========================
First_Name = "Juntao"
Last_Name = "Yu"
Email = "yujuntao1993@gmail.com"
Mobile = "0474836509"

Domestic_or_International = "International"
Postgrad_or_Undergrad = "Postgraduate"

# =========================
# --- Booking Function ---
# =========================
def job(slot):
    today = datetime.today().day
    driver = Driver(uc=True)  
    driver.keep_alive = True

    driver.get("https://events.humanitix.com/food-hub-2026-semester-1/tickets?c=app")

    try:
        # --- Select date ---
        date_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
        )
        date_button.click()

        # --- Select time ---
        # 这里的 slot 会直接使用下面调用时传入的参数
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
            print(f"Booking for {slot} succeeded!")
            # driver.quit() # 测试时可以注释掉这一行，方便查看结果
            return
        except:
            print(f"Booking flow for {slot} did not reach success page.")

    except Exception as e:
        print(f"Failed for {slot}. Error: {e}")

# ==================================
# --- Test Execution (Immediate) ---
# ==================================
if __name__ == "__main__":
    # 在这里输入你想测试的那个时间段文字
    # 比如你想测试半小时的，就改写成 "10:30am"
    test_slot = "2:00pm" 
    
    print(f"Starting test for slot: {test_slot}")
    job(test_slot)