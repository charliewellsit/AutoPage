from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import multiprocessing
import os
import schedule
import shutil
import subprocess
import tempfile
from datetime import datetime
import time


BOOKING_URL = "https://events.humanitix.com/food-hub-2026-semester-1b/tickets"
WAIT_TIMEOUT = 60
HOLD_BROWSER_ON_ERROR = True

USER_1 = ("Juntao", "Yu", "yujuntao1993@gmail.com", "0474836509", "International", "Postgraduate", "No", "juntao")
USER_2 = ("YING", "QI", "brittanysimon71@gmail.com", "0460737966", "International", "Postgraduate", "No", "yingqi")

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
    try:
        subprocess.Popen(["caffeinate", "-u", "-t", "2"])
    except Exception as e:
        print(f"无法启动 caffeinate: {e}")


def keep_display_awake_while_running():
    try:
        return subprocess.Popen(["caffeinate", "-d", "-i", "-w", str(os.getpid())])
    except Exception as e:
        print(f"无法启动 caffeinate: {e}")
        return None


def create_driver(session_name):
    session_dir = tempfile.mkdtemp(prefix=f"autopage_js_{session_name}_")
    driver = Driver(uc=True, user_data_dir=session_dir)
    driver.keep_alive = True
    return driver, session_dir


def cleanup_driver(driver, session_dir):
    try:
        driver.quit()
    except Exception:
        pass
    shutil.rmtree(session_dir, ignore_errors=True)


def click_date_button_via_javascript(driver, day):
    return driver.execute_script(
        """
        const target = String(arguments[0]).trim();
        const buttons = Array.from(document.querySelectorAll("button"));
        const match = buttons.find((button) => {
            const text = (button.textContent || "").replace(/\\s+/g, " ").trim();
            return text.includes(target);
        });

        if (!match) {
            return false;
        }

        match.scrollIntoView({ block: "center", inline: "center" });
        match.focus();
        match.click();
        return true;
        """,
        day,
    )


def click_time_button_via_javascript(driver, slot):
    return driver.execute_script(
        """
        const target = arguments[0];
        const normalize = (value) => (value || "").replace(/\\s+/g, " ").trim();
        const buttons = Array.from(document.querySelectorAll("button.dropdown-pill.available"));
        const match = buttons.find((button) => normalize(button.textContent) === target);

        if (!match) {
            return false;
        }

        match.scrollIntoView({ block: "center", inline: "center" });
        match.focus();

        if (window.PointerEvent) {
            ["pointerover", "pointerdown", "pointerup"].forEach((type) => {
                match.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true }));
            });
        }

        ["mouseover", "mousedown", "mouseup", "click"].forEach((type) => {
            match.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
        });

        return true;
        """,
        slot,
    )


def click_selector_via_javascript(driver, selector):
    return driver.execute_script(
        """
        const target = document.querySelector(arguments[0]);
        if (!target) {
            return false;
        }

        target.scrollIntoView({ block: "center", inline: "center" });
        if (typeof target.focus === "function") {
            target.focus();
        }

        if (window.PointerEvent) {
            ["pointerover", "pointerdown", "pointerup"].forEach((type) => {
                target.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true }));
            });
        }

        ["mouseover", "mousedown", "mouseup", "click"].forEach((type) => {
            target.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
        });

        return true;
        """,
        selector,
    )


def click_dropdown_option_via_javascript(driver, label_hint, value):
    dropdown_opened = driver.execute_script(
        """
        const hint = (arguments[0] || "").toLowerCase();
        const normalize = (text) => (text || "").replace(/\\s+/g, " ").trim().toLowerCase();

        const dispatchClick = (target) => {
            target.scrollIntoView({ block: "center", inline: "center" });
            if (typeof target.focus === "function") {
                target.focus();
            }

            if (window.PointerEvent) {
                ["pointerover", "pointerdown", "pointerup"].forEach((type) => {
                    target.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true }));
                });
            }

            ["mouseover", "mousedown", "mouseup", "click"].forEach((type) => {
                target.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
            });

            if (typeof target.click === "function") {
                target.click();
            }
        };

        const labels = Array.from(document.querySelectorAll(".AdditionalQuestionField label, .Select label"));
        const label = labels.find((item) => normalize(item.textContent).includes(hint));
        if (!label) {
            return false;
        }

        const comboboxId = label.getAttribute("for");
        const combobox = comboboxId ? document.getElementById(comboboxId) : null;
        if (!combobox) {
            return false;
        }

        dispatchClick(combobox);
        return combobox.getAttribute("aria-controls") || false;
        """,
        label_hint,
    )
    if not dropdown_opened:
        return False

    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda current_driver: current_driver.execute_script(
            """
            const listboxId = arguments[0];
            const listbox = document.getElementById(listboxId);
            if (!listbox) {
                return false;
            }
            return listbox.getAttribute("data-open") === "true";
            """,
            dropdown_opened,
        )
    )

    return driver.execute_script(
        """
        const listboxId = arguments[0];
        const target = arguments[1];
        const normalize = (text) => (text || "").replace(/\\s+/g, " ").trim();

        const dispatchClick = (node) => {
            node.scrollIntoView({ block: "center", inline: "center" });
            if (typeof node.focus === "function") {
                node.focus();
            }

            if (window.PointerEvent) {
                ["pointerover", "pointerdown", "pointerup"].forEach((type) => {
                    node.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true }));
                });
            }

            ["mouseover", "mousedown", "mouseup", "click"].forEach((type) => {
                node.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
            });

            if (typeof node.click === "function") {
                node.click();
            }
        };

        const listbox = document.getElementById(listboxId);
        if (!listbox) {
            return false;
        }

        const option = Array.from(listbox.querySelectorAll("[role='option']"))
            .find((item) => normalize(item.textContent) === target);
        if (!option) {
            return false;
        }

        dispatchClick(option);

        const comboboxId = listboxId.replace(/-controls$/, "");
        const combobox = document.getElementById(comboboxId);
        const fieldContent = combobox?.querySelector("[data-testid='field-content']");
        const selectedText = normalize(fieldContent?.textContent);
        return selectedText === target;
        """,
        dropdown_opened,
        value,
    )


def hold_browser_open_on_error(session_name):
    print(f"{session_name} 浏览器将保持打开，方便检查页面。手动停止脚本后才会关闭。")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass


def fill_single_booking(trigger_time, slot, first_name, last_name, email, mobile, domestic_or_international, postgrad_or_undergrad, usu_member, session_name):
    today = datetime.today().day
    driver, session_dir = create_driver(session_name)
    should_hold_on_error = False

    print(f"[{datetime.now()}] {session_name} 正在预加载并锁定时间段: {slot}")
    driver.get(BOOKING_URL)
    driver.execute_script("document.body.style.zoom='50%'")

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda current_driver: current_driver.execute_script(
                """
                return Array.from(document.querySelectorAll("button"))
                    .some((button) => ((button.textContent || "").replace(/\\s+/g, " ").trim()).includes(arguments[0]));
                """,
                str(today),
            )
        )
        if not click_date_button_via_javascript(driver, today):
            raise Exception(f"{session_name} 无法选择日期 {today}")

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda current_driver: current_driver.execute_script(
                """
                return Array.from(document.querySelectorAll("button.dropdown-pill.available"))
                    .some((button) => ((button.textContent || "").replace(/\\s+/g, " ").trim()) === arguments[0]);
                """,
                slot,
            )
        )
        if not click_time_button_via_javascript(driver, slot):
            raise Exception(f"{session_name} 无法选择时间 {slot}")
        print(f"{session_name} 时间已锁定，等待准点刷新...")

        while True:
            if datetime.now().strftime("%H:%M:%S") >= trigger_time:
                break
            time.sleep(0.05)

        print(f"[{datetime.now()}] {session_name} 准点！正在刷新页面激活加号...")
        driver.refresh()
        driver.execute_script("document.body.style.zoom='50%'")

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda current_driver: current_driver.execute_script(
                """
                const plus = document.querySelector("div.plus[data-disabled='false']");
                return !!plus;
                """
            )
        )
        if not click_selector_via_javascript(driver, "div.plus[data-disabled='false']"):
            raise Exception(f"{session_name} 无法点击加号")

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda current_driver: current_driver.execute_script(
                """
                return !!document.querySelector("button[data-testid='checkout-btn'][aria-disabled='false']");
                """
            )
        )
        if not click_selector_via_javascript(driver, "button[data-testid='checkout-btn'][aria-disabled='false']"):
            raise Exception(f"{session_name} 无法点击 Continue")

        driver.execute_script("document.body.style.zoom='50%'")

        driver.uc_gui_click_captcha()
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, "firstName"))).send_keys(first_name)
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, "lastName"))).send_keys(last_name)
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(email)
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, "mobile"))).send_keys(mobile)

        time.sleep(1)
        if not click_selector_via_javascript(driver, "button[data-testid='buyer-info-submit']"):
            raise Exception(f"{session_name} 无法点击买家信息提交按钮")

        for label, value in [
            ("domestic or international", domestic_or_international),
            ("postgraduate or undergraduate", postgrad_or_undergrad),
            ("USU member", usu_member),
        ]:
            if not click_dropdown_option_via_javascript(driver, label, value):
                raise Exception(f"{session_name} 无法选择下拉项 {label} -> {value}")

        if not click_selector_via_javascript(driver, "button[data-testid='ticket-info-submit']"):
            raise Exception(f"{session_name} 无法提交附加问题")

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.any_of(
                EC.url_contains("complete"),
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'View ticket')]")),
            )
        )
        print(f"恭喜！{session_name} 的 {slot} 预订成功。")

    except Exception as e:
        print(f"{session_name} 流程出错: {e}")
        should_hold_on_error = True

    finally:
        if should_hold_on_error and HOLD_BROWSER_ON_ERROR:
            hold_browser_open_on_error(session_name)
        cleanup_driver(driver, session_dir)


def run_both(trigger_time, slot):
    p1 = multiprocessing.Process(target=fill_single_booking, args=(trigger_time, slot, *USER_1))
    p2 = multiprocessing.Process(target=fill_single_booking, args=(trigger_time, slot, *USER_2))

    p1.start()
    time.sleep(2)
    p2.start()


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    wake_display_now()
    keep_display_awake_while_running()

    for warmup_time, trigger_time, slot in BOOKING_SCHEDULES:
        schedule.every().day.at(warmup_time).do(run_both, trigger_time, slot)

    while True:
        schedule.run_pending()
        time.sleep(1)
