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

Domestic_or_International = "International"
Postgrad_or_Undergrad = "Postgraduate"

# =========================
# --- Booking Function ---
# =========================
def job(trigger_time, slot):
    """
    trigger_time: 抢票启动的精确秒数 (如 "10:00:00")
    slot: 预选的时间段 (如 "12:00pm")
    """
    today = datetime.today().day
    driver = Driver(uc=True)  
    driver.keep_alive = True

    # --- 阶段 1：预热 (提前进入并选好时间) ---
    print(f"[{datetime.now()}] 正在预加载并锁定时间段: {slot}")
    driver.get("https://events.humanitix.com/food-hub-2026-semester-1/tickets?c=app")
    
    try:
        # 预选日期
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))).click()
        # 预选时间点
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{slot}']"))).click()
        print("时间已锁定，等待准点刷新...")

        # --- 阶段 2：等待准点 ---
        while True:
            if datetime.now().strftime("%H:%M:%S") >= trigger_time:
                break
            time.sleep(0.05) # 高频检查

        # --- 阶段 3：冲刺 (准点刷新并直接点加号) ---
        print(f"[{datetime.now()}] 准点！正在刷新页面激活加号...")
        driver.refresh()

        # 直接等待并点击加号 (跳过选日期和时间步骤)
        plus_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']"))
        )
        driver.execute_script("arguments[0].click();", plus_button)

        # 点击结算
        continue_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']"))
        )
        driver.execute_script("arguments[0].click();", continue_button)

        # --- 后续信息填充 (保持原有结构) ---
        driver.uc_gui_click_captcha()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "firstName"))).send_keys(First_Name)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "lastName"))).send_keys(Last_Name)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(Email)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "mobile"))).send_keys(Mobile)

        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))).click()

        # 下拉框
        for label, val in [("domestic or international", Domestic_or_International), ("postgraduate or undergraduate", Postgrad_or_Undergrad)]:
            dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//label/span[contains(text(),'{label}')]/ancestor::div[contains(@class,'Select')]//div[@role='combobox']")))
            dropdown.click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and normalize-space()='{val}']"))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='ticket-info-submit']"))).click()

        # 成功校验
        WebDriverWait(driver, 30).until(EC.any_of(EC.url_contains("complete"), EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'View ticket')]"))))
        print(f"恭喜！{slot} 预订成功。")
        schedule.clear()
        
    except Exception as e:
        print(f"流程出错: {e}")

# =========================
# --- Scheduler ---
# =========================
# 设定在抢票时间前 1 分钟启动准备程序 (例如 8:00 抢，则 7:59 启动)
schedule.every().day.at("07:59").do(job, "08:00:00", "10:00am")
schedule.every().day.at("08:29").do(job, "08:30:00", "10:30am")
schedule.every().day.at("08:59").do(job, "09:00:00", "11:00am")
schedule.every().day.at("09:29").do(job, "09:30:00", "11:30am")
schedule.every().day.at("09:59").do(job, "10:00:00", "12:00pm")
schedule.every().day.at("10:29").do(job, "10:30:00", "12:30pm")
schedule.every().day.at("10:59").do(job, "11:00:00", "1:00pm")
schedule.every().day.at("11:29").do(job, "11:30:00", "1:30pm")
schedule.every().day.at("11:59").do(job, "12:00:00", "2:00pm")
schedule.every().day.at("12:29").do(job, "12:30:00", "2:30pm")

while True:
    schedule.run_pending()
    time.sleep(1)