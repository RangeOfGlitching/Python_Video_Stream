import pyrealsense2 as rs
import numpy as np
import cv2
from datetime import datetime


pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth,1280,720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
# (1280,720)

now = datetime.now()
current_time = now.strftime("%H_%M_%S")
color_path = current_time + '_rgb.avi'
depth_path = current_time + '_depth.avi'

colorWriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 25, (1280, 720), 1)
# depthWriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480), 1)

pipeline.start(config)

try:
    while True:
        frames = pipeline.wait_for_frames()
        # depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        # if not depth_frame or not color_frame:
        #     continue
        if not color_frame:
            continue

        # convert images to numpy arrays
        # depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

       
        color_image = cv2.rotate(color_image, cv2.ROTATE_180) #rotate image
        # depthWriter.write(depth_colormap)
        colorWriter.write(color_image)

        # cv2.imshow('Stream', color_image)

        # if cv2.waitKey(1) == ord("q"):
        #     break
finally:
    colorWriter.release()
    # depthWriter.release()
    pipeline.stop()
