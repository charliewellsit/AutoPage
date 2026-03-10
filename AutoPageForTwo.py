from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from datetime import datetime
import time
import threading

# =========================
# --- 用户信息配置列表 ---
# =========================
# 在这里管理所有需要抢票的账号，加几个人就写几个字典
USERS = [
    {
        "profile": "profile_juntao", # 独立的浏览器缓存文件夹名
        "First_Name": "Juntao",
        "Last_Name": "Yu",
        "Email": "yujuntao1993@gmail.com",
        "Mobile": "0474836509",
        "Domestic_or_International": "International",
        "Postgrad_or_Undergrad": "Postgraduate"
    },
    {
        "profile": "profile_ying",   # 独立的浏览器缓存文件夹名
        "First_Name": "YING",
        "Last_Name": "QI",
        "Email": "brittanysimon71@gmail.com",
        "Mobile": "0460737966",
        "Domestic_or_International": "International",
        "Postgrad_or_Undergrad": "Postgraduate"
    }
]

# =========================
# --- 核心抢票逻辑 ---
# =========================
def execute_booking(user, trigger_time, slot):
    today = datetime.today().day
    # 动态分配独立的 profile，防止两个浏览器抢夺同一个缓存导致崩溃
    driver = Driver(uc=True, user_data_dir=user["profile"])  
    driver.keep_alive = True

    name = user["First_Name"]
    print(f"[{datetime.now()}] [{name}] 正在预加载并锁定时间段: {slot}")
    
    try:
        driver.get("https://events.humanitix.com/food-hub-2026-semester-1/tickets?c=app")
        driver.execute_script("document.body.style.zoom='50%'")
        
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))).click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{slot}']"))).click()
        print(f"[{name}] 时间已锁定，等待准点 {trigger_time} 刷新...")

        # --- 等待准点 ---
        while True:
            if datetime.now().strftime("%H:%M:%S") >= trigger_time:
                break
            time.sleep(0.05) 

        # --- 冲刺 ---
        print(f"[{datetime.now()}] [{name}] 准点！正在刷新页面激活加号...")
        driver.refresh()
        
        plus_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']"))
        )
        driver.execute_script("arguments[0].click();", plus_button)

        continue_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']"))
        )
        driver.execute_script("arguments[0].click();", continue_button)

        # 填写当前线程对应的用户信息
        driver.uc_gui_click_captcha()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "firstName"))).send_keys(user["First_Name"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "lastName"))).send_keys(user["Last_Name"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(user["Email"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "mobile"))).send_keys(user["Mobile"])

        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))).click()

        for label, val in [("domestic or international", user["Domestic_or_International"]), ("postgraduate or undergraduate", user["Postgrad_or_Undergrad"])]:
            dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//label/span[contains(text(),'{label}')]/ancestor::div[contains(@class,'Select')]//div[@role='combobox']")))
            dropdown.click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and normalize-space()='{val}']"))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='ticket-info-submit']"))).click()

        WebDriverWait(driver, 30).until(EC.any_of(EC.url_contains("complete"), EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'View ticket')]"))))
        print(f"恭喜！[{name}] 的 {slot} 预订成功。")
        schedule.clear()
        
    except Exception as e:
        print(f"[{name}] 流程出错: {e}")

# =========================
# --- 线程管理器 ---
# =========================
def job_for_all_users(trigger_time, slot):
    threads = []
    for user in USERS:
        # 为每个人分配一个独立的虚拟操作员（线程）
        t = threading.Thread(target=execute_booking, args=(user, trigger_time, slot))
        threads.append(t)
        t.start()
        
        # 【重要安全机制】错开 1.5 秒启动浏览器。
        # SeleniumBase 启动时会修改底层文件，如果两个并发线程在同一毫秒修改文件会报错。
        # 这个错开是在“预加载阶段”（如 07:59:00 和 07:59:01），绝对不会影响 08:00:00 的同时抢票冲刺。
        time.sleep(1.5) 

    # 等待所有人的操作结束
    for t in threads:
        t.join()

# =========================
# --- 定时器 ---
# =========================
schedule.every().day.at("07:59").do(job_for_all_users, "08:00:00", "10:00am")
schedule.every().day.at("08:29").do(job_for_all_users, "08:30:00", "10:30am")
schedule.every().day.at("08:59").do(job_for_all_users, "09:00:00", "11:00am")
schedule.every().day.at("09:29").do(job_for_all_users, "09:30:00", "11:30am")
schedule.every().day.at("09:59").do(job_for_all_users, "10:00:00", "12:00pm")
schedule.every().day.at("10:29").do(job_for_all_users, "10:30:00", "12:30pm")
schedule.every().day.at("10:59").do(job_for_all_users, "11:00:00", "1:00pm")
schedule.every().day.at("11:29").do(job_for_all_users, "11:30:00", "1:30pm")
schedule.every().day.at("11:59").do(job_for_all_users, "12:00:00", "2:00pm")
schedule.every().day.at("12:29").do(job_for_all_users, "12:30:00", "2:30pm")

print("双账号抢票程序已启动，等待定时任务触发...")

while True:
    schedule.run_pending()
    time.sleep(1)