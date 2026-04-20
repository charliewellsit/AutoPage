from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import os
import schedule
import subprocess
from datetime import datetime
import time


BOOKING_URL = "https://events.humanitix.com/food-hub-2026-semester-1b/tickets"

# 这些值会直接填入结账页表单；只抢 Juntao 这一张票时改这里即可。
First_Name = "Juntao"
Last_Name = "Yu"
Email = "yujuntao1993@gmail.com"
Mobile = "0474836509"
Domestic_or_International = "International"
Postgrad_or_Undergrad = "Postgraduate"
USU_Member = "No"

# 每一项分别是：预热启动时间、真正点击开抢的时间、页面里对应的场次文本。
BOOKING_SCHEDULES = [
    ("07:59", "08:00:00", "10:00am"),
    ("08:29", "08:30:00", "10:30am"),
    ("08:59", "09:00:00", "11:00am"),
    ("09:29", "09:30:00", "11:30am"),
    ("09:59", "10:00:00", "12:00pm"),
    ("10:29", "10:30:00", "12:30pm"),
    ("10:59", "11:00:00", "1:00pm"),
    ("11:29", "11:30:00", "1:30pm"),
    ("11:59", "12:00:00", "2:00pm"),
    ("12:29", "12:30:00", "2:30pm"),
]


def wake_display_now():
    # 如果显示器已经灭了，这里先尝试点亮它。
    try:
        subprocess.Popen(["caffeinate", "-u", "-t", "2"])
    except Exception as e:
        print(f"无法启动 caffeinate: {e}")


def keep_display_awake_while_running():
    # 让当前脚本存活的整个期间都不进入显示器睡眠或空闲睡眠。
    try:
        subprocess.Popen(["caffeinate", "-d", "-i", "-w", str(os.getpid())])
    except Exception as e:
        print(f"无法启动 caffeinate: {e}")


def job(trigger_time, slot):
    today = datetime.today().day
    driver = Driver(uc=True)
    driver.keep_alive = True

    print(f"[{datetime.now()}] 正在预加载并锁定时间段: {slot}")
    driver.get(BOOKING_URL)

    # 页面缩小后，票档区域和底部 Continue 更容易同时留在视野里。
    driver.execute_script("document.body.style.zoom='50%'")

    try:
        # 先点当天日期，让页面只显示当天可抢的场次。
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{today}')]"))
        ).click()

        # 再提前点好目标场次，真正开票时只需要 refresh 和加号两步。
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{slot}']"))
        ).click()
        print("时间已锁定，等待准点刷新...")

        # 用短轮询贴近 trigger_time，避免在最后一秒睡过头。
        while True:
            if datetime.now().strftime("%H:%M:%S") >= trigger_time:
                break
            time.sleep(0.05)

        print(f"[{datetime.now()}] 准点！正在刷新页面激活加号...")
        driver.refresh()

        # 页面刷新后直接等待加号可点，然后立刻加 1 张票。
        plus_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'plus') and @data-disabled='false']"))
        )
        driver.execute_script("arguments[0].click();", plus_button)

        # 数量加上去后，继续点击结账按钮进入信息页。
        continue_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-testid='checkout-btn' and @aria-disabled='false']"))
        )
        driver.execute_script("arguments[0].click();", continue_button)

        # refresh 后缩放会失效，所以进入信息页前再缩一次。
        driver.execute_script("document.body.style.zoom='50%'")

        # 如果页面弹出验证码，这一步会把交互焦点带到验证码位置，方便你手动确认。
        driver.uc_gui_click_captcha()

        # 买家信息这四项都有稳定 id，直接按 id 填写最接近你原来成功的写法。
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "firstName"))
        ).send_keys(First_Name)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "lastName"))
        ).send_keys(Last_Name)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        ).send_keys(Email)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mobile"))
        ).send_keys(Mobile)

        # 留一点时间给页面完成前端校验，再点下一步。
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='buyer-info-submit']"))
        ).click()

        # 这三道问卷都在同一类下拉组件里，所以继续沿用你原来那套定位方式。
        for label, val in [
            ("domestic or international", Domestic_or_International),
            ("postgraduate or undergraduate", Postgrad_or_Undergrad),
            ("Are you USU member?", USU_Member),
        ]:
            dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//label/span[contains(text(),'{label}')]/ancestor::div[contains(@class,'Select')]//div[@role='combobox']",
                    )
                )
            )
            dropdown.click()
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//div[@role='option' and normalize-space()='{val}']",
                    )
                )
            ).click()

        # 提交问卷后，进入成功页或出现 View ticket 按钮都算抢票成功。
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='ticket-info-submit']"))
        ).click()
        WebDriverWait(driver, 30).until(
            EC.any_of(
                EC.url_contains("complete"),
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'View ticket')]")),
            )
        )
        print(f"恭喜！{slot} 预订成功。")
        schedule.clear()

    except Exception as e:
        print(f"流程出错: {e}")


def register_daily_jobs():
    for warmup_time, trigger_time, slot in BOOKING_SCHEDULES:
        schedule.every().day.at(warmup_time).do(job, trigger_time, slot)


if __name__ == "__main__":
    # 从脚本启动开始就保持屏幕常亮，这样即使离开一小时等开票，也不会先被系统锁屏。
    wake_display_now()
    keep_display_awake_while_running()

    parser = argparse.ArgumentParser()
    parser.add_argument("--once", nargs=2, metavar=("TRIGGER_TIME", "SLOT"))
    args = parser.parse_args()

    # 双人脚本会用 --once 启动单人脚本，这样每个单人脚本都还是走它原本那套成功流程。
    if args.once:
        job(args.once[0], args.once[1])
    else:
        register_daily_jobs()
        while True:
            schedule.run_pending()
            time.sleep(1)
