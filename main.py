# main.py
import threading
import time
import voice.command_listener as cl             # ← 모듈 통째로 임포트
from control.robot_control import robot_main_loop, set_robot_enabled

def command_monitor_loop():
    last_id = None
    while True:
        current_id = cl.latest_command_id       # ← 매번 모듈 속 변수 읽기
        if current_id != last_id:
            last_id = current_id
            if current_id == 1:
                print("▶️  로봇 START (ID=1)")
                set_robot_enabled(True)
            elif current_id == 2:
                print("⏸️  로봇 STOP  (ID=2)")
                set_robot_enabled(False)
            else:
                print(f"ℹ️  ID={current_id} (무시)")
        time.sleep(0.05)

def main():
    print("🚀  시스템 전체 시작")
    threading.Thread(target=cl.voice_command_loop, daemon=True).start()
    threading.Thread(target=command_monitor_loop, daemon=True).start()
    robot_main_loop()

if __name__ == "__main__":
    main()
