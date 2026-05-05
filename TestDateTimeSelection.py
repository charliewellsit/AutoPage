from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime


BOOKING_URL = "https://events.humanitix.com/food-hub-2026-semester-1b/tickets"
TEST_DAY = datetime.today().day
TEST_SLOT = "10:00am"
WAIT_TIMEOUT = 60

# 可选值: "selenium"、"javascript" 或 "actions"
DATE_CLICK_MODE = "javascript"
TIME_CLICK_MODE = "actions"


def click_element(driver, element, mode):
    if mode == "javascript":
        driver.execute_script("arguments[0].click();", element)
    elif mode == "actions":
        ActionChains(driver).move_to_element(element).pause(0.1).click().perform()
    else:
        element.click()


def click_time_button_via_javascript(driver, slot):
    return driver.execute_script(
        """
        const target = arguments[0];
        const normalize = (value) => (value || "").replace(/\\s+/g, " ").trim();
        const buttons = Array.from(document.querySelectorAll("button.dropdown-pill.available"));
        const texts = buttons.map((button) => normalize(button.textContent));
        const match = buttons.find((button) => normalize(button.textContent) === target);

        if (!match) {
            return { ok: false, texts };
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

        return { ok: true, texts };
        """,
        slot,
    )


def main():
    driver = Driver(uc=True)
    driver.keep_alive = True

    print(f"[{datetime.now()}] 打开页面: {BOOKING_URL}")
    driver.get(BOOKING_URL)
    driver.execute_script("document.body.style.zoom='50%'")

    try:
        date_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{TEST_DAY}')]"))
        )
        click_element(driver, date_button, DATE_CLICK_MODE)
        print(f"日期已选择: {TEST_DAY} 号, 点击方式: {DATE_CLICK_MODE}")

        time_buttons = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.dropdown-pill.available"))
        )
        time_texts = [button.text.strip() for button in time_buttons]
        print(f"页面里检测到的时间按钮: {time_texts}")

        if TIME_CLICK_MODE == "javascript":
            result = click_time_button_via_javascript(driver, TEST_SLOT)
            print(f"页面里检测到的时间按钮: {result['texts']}")
            if not result["ok"]:
                raise Exception(f"没有找到时间按钮: {TEST_SLOT}")
        else:
            time_button = None
            for button in time_buttons:
                if button.text.strip() == TEST_SLOT:
                    time_button = button
                    break

            if time_button is None:
                raise Exception(f"没有找到时间按钮: {TEST_SLOT}")

            click_element(driver, time_button, TIME_CLICK_MODE)

        print(f"时间已选择: {TEST_SLOT}, 点击方式: {TIME_CLICK_MODE}")
        print("测试完成。请确认页面上日期和时间是否都已被选中。")

    except Exception as e:
        print(f"测试出错: {e}")

    input("按 Enter 关闭浏览器...")
    driver.quit()


if __name__ == "__main__":
    main()
