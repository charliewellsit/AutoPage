import os
import subprocess
import sys
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JUNTAO_SCRIPT = os.path.join(BASE_DIR, "AutoPageChromeByPass_JuntaoYu.py")
YINGQI_SCRIPT = os.path.join(BASE_DIR, "AutoPageChromeByPass_YingQi.py")
PROFILE_DIR_ENV = "AUTOPAGE_PROFILE_DIR"
PROFILE_BASE_DIR = os.path.join(BASE_DIR, ".browser_profiles")


def keep_display_awake_while_running():
    try:
        return subprocess.Popen(["caffeinate", "-d", "-i", "-w", str(os.getpid())])
    except Exception as e:
        print(f"无法启动 caffeinate: {e}")
        return None


def launch_script(script_path, profile_name):
    env = os.environ.copy()
    env[PROFILE_DIR_ENV] = os.path.join(PROFILE_BASE_DIR, profile_name)
    return subprocess.Popen([sys.executable, script_path], cwd=BASE_DIR, env=env)


if __name__ == "__main__":
    keep_display_awake_while_running()

    p1 = launch_script(JUNTAO_SCRIPT, "juntao")
    time.sleep(2)
    p2 = launch_script(YINGQI_SCRIPT, "yingqi")

    print(f"已启动 Juntao 进程 PID={p1.pid}")
    print(f"已启动 YingQi 进程 PID={p2.pid}")

    p1.wait()
    p2.wait()
