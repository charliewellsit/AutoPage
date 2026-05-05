from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime


BOOKING_URL = "https://events.humanitix.com/food-hub-2026-semester-1b/tickets"
TEST_DAY = datetime.today().day
TEST_SLOT = "10:00am"
WAIT_TIMEOUT = 60


def click_date_button_via_javascript(driver, day):
    return driver.execute_script(
        """
        const target = String(arguments[0]).trim();
        const buttons = Array.from(document.querySelectorAll("button"));
        const texts = buttons.map((button) => (button.textContent || "").replace(/\\s+/g, " ").trim());
        const match = buttons.find((button) => {
            const text = (button.textContent || "").replace(/\\s+/g, " ").trim();
            return text.includes(target);
        });

        if (!match) {
            return { ok: false, texts };
        }

        match.scrollIntoView({ block: "center", inline: "center" });
        match.focus();
        match.click();
        return { ok: true, texts };
        """,
        day,
    )


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
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda current_driver: current_driver.execute_script(
                """
                return Array.from(document.querySelectorAll("button"))
                    .some((button) => ((button.textContent || "").replace(/\\s+/g, " ").trim()).includes(arguments[0]));
                """,
                str(TEST_DAY),
            )
        )
        date_result = click_date_button_via_javascript(driver, TEST_DAY)
        print(f"页面里检测到的日期按钮文本数量: {len(date_result['texts'])}")
        if not date_result["ok"]:
            raise Exception(f"没有找到日期按钮: {TEST_DAY}")
        print(f"日期已选择: {TEST_DAY} 号, 点击方式: javascript")

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda current_driver: current_driver.execute_script(
                """
                return Array.from(document.querySelectorAll("button.dropdown-pill.available"))
                    .some((button) => ((button.textContent || "").replace(/\\s+/g, " ").trim()) === arguments[0]);
                """,
                TEST_SLOT,
            )
        )
        time_result = click_time_button_via_javascript(driver, TEST_SLOT)
        print(f"页面里检测到的时间按钮: {time_result['texts']}")
        if not time_result["ok"]:
            raise Exception(f"没有找到时间按钮: {TEST_SLOT}")
        print(f"时间已选择: {TEST_SLOT}, 点击方式: javascript")
        print("测试完成。请确认页面上日期和时间是否都已被选中。")

    except Exception as e:
        print(f"测试出错: {e}")

    input("按 Enter 关闭浏览器...")
    driver.quit()


if __name__ == "__main__":
    main()
