"""
손 추적 + PID 로봇팔 제어 루프.
robot_enabled 가 False 이면 서보 명령을 보내지 않고 대기한다.
set_robot_enabled() 로 외부에서 on/off 제어.
"""
import time
import cv2
import numpy as np
import pyrealsense2 as rs
import mediapipe as mp
import Arm_Lib
import PID

# ── 전역 상태 ─────────────────────────────────
robot_enabled = False                 # 외부에서 on / off
arm          = Arm_Lib.Arm_Device()

# 초기 자세(안전)
INIT_ANGLES  = [90, 135, 45, 45, 90, 30]

# ── 비전 / PID 세팅 ──────────────────────────
mp_hands = mp.solutions.hands
hands    = mp_hands.Hands(max_num_hands=1)

pid_x = PID.PositionalPID(0.8, 0.0, 0.1)
pid_y = PID.PositionalPID(0.8, 0.0, 0.1)

target_x, target_y = 90, 60   # 서보1·3 기준각

# RealSense 파이프라인
pipe   = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
profile      = pipe.start(config)
depth_scale  = profile.get_device().first_depth_sensor().get_depth_scale()

# ── API ───────────────────────────────────────
def set_robot_enabled(enabled: bool):
    """main.py 에서 호출"""
    global robot_enabled
    robot_enabled = enabled

def robot_main_loop():
    global target_x, target_y

    print("🤖  로봇 추적 루프 시작")
    # 부드럽게 초기화
    arm.Arm_serial_servo_write6_array(INIT_ANGLES, 1000)
    time.sleep(1.2)

    try:
        while True:
            frames = pipe.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            if not (color_frame and depth_frame):
                continue

            color_img = np.asanyarray(color_frame.get_data())
            img_rgb   = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)
            results   = hands.process(img_rgb)

            # ── 동작 ON/OFF 확인 ──────────────
            if not robot_enabled:
                cv2.imshow("Hand Tracker", color_img)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                time.sleep(0.03)
                continue

            # ── 손 추적 & 서보 제어 ───────────
            if results.multi_hand_landmarks and results.multi_handedness:
                label = results.multi_handedness[0].classification[0].label
                if label != "Left":                # 실제 오른손
                    lm   = results.multi_hand_landmarks[0].landmark[0]
                    h, w = color_img.shape[:2]
                    px, py = int(lm.x * w), int(lm.y * h)

                    if 0 <= px < w and 0 <= py < h:
                        depth_mm = depth_frame.get_distance(px, py)*1000.0
                        cv2.circle(color_img, (px, py), 8, (0,255,0), -1)

                        pid_x.SystemOutput = px
                        pid_y.SystemOutput = py
                        pid_x.SetStepSignal(w//2)
                        pid_y.SetStepSignal(h//2)
                        pid_x.SetInertiaTime(0.01, 0.1)
                        pid_y.SetInertiaTime(0.01, 0.1)

                        target_x += pid_x.SystemOutput*0.03
                        target_y += pid_y.SystemOutput*0.03
                        target_x = max(0,   min(180, int(target_x)))
                        target_y = max(0,   min(180, int(target_y)))

                        angles = [target_x, 135, target_y/2, target_y/2, 90, 30]
                        arm.Arm_serial_servo_write6_array(angles, 150)

                        cv2.putText(color_img,
                                    f"x:{px} y:{py} z:{depth_mm:.1f}mm",
                                    (px+10, py-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0,255,0), 2)

            cv2.imshow("Hand Tracker", color_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipe.stop()
        cv2.destroyAllWindows()
