import os
import json
import schedule
import subprocess
import sys
from datetime import datetime
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JUNTAO_SCRIPT = os.path.join(BASE_DIR, "AutoPageChromeByPass_JuntaoYu.py")
YINGQI_SCRIPT = os.path.join(BASE_DIR, "AutoPageChromeByPass_YingQi.py")

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
    # 双人启动器本身会常驻，所以把显示器保持唤醒绑定到当前进程生命周期即可。
    try:
        subprocess.Popen(["caffeinate", "-d", "-i", "-w", str(os.getpid())])
    except Exception as e:
        print(f"无法启动 caffeinate: {e}")


def launch_single_script_in_terminal(script_path, trigger_time, slot):
    # 这里直接打开新的 Terminal 会话来跑单人脚本，尽量贴近你手动开两个 terminal 的成功方式。
    command = (
        f"cd {BASE_DIR!r} && "
        f"{sys.executable!r} {script_path!r} --once {trigger_time!r} {slot!r}"
    )
    applescript = f'tell application "Terminal" to do script {json.dumps(command)}'
    return subprocess.Popen(["osascript", "-e", applescript], cwd=BASE_DIR)


def run_both(trigger_time, slot):
    print(f"[{datetime.now()}] 正在启动两个独立抢票进程: {slot}")

    # 每个用户都在独立 Terminal 会话中运行，这样报错不会一闪而过，也更接近你手动验证成功的流程。
    p1 = launch_single_script_in_terminal(JUNTAO_SCRIPT, trigger_time, slot)
    p2 = launch_single_script_in_terminal(YINGQI_SCRIPT, trigger_time, slot)

    print(
        f"[{datetime.now()}] 已启动 Juntao 进程 PID={p1.pid}，"
        f"YingQi 进程 PID={p2.pid}"
    )


def register_daily_jobs():
    for warmup_time, trigger_time, slot in BOOKING_SCHEDULES:
        schedule.every().day.at(warmup_time).do(run_both, trigger_time, slot)


if __name__ == "__main__":
    # 从你点击运行双人脚本开始，就一直保持显示器常亮，直到你手动结束脚本。
    wake_display_now()
    keep_display_awake_while_running()

    register_daily_jobs()

    while True:
        schedule.run_pending()
        time.sleep(1)
