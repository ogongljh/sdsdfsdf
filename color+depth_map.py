import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os

# 저장 디렉토리 생성
os.makedirs("output", exist_ok=True)

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

try:
    for i in range(10):  # 10장만 캡처
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
        )

        # 저장
        cv2.imwrite(f"output/color_{i}.png", color_image)
        cv2.imwrite(f"output/depth_{i}.png", depth_colormap)
        print(f"[INFO] Saved image {i}")
        time.sleep(1)

finally:
    pipeline.stop()
    print("[INFO] Finished capturing images.")
