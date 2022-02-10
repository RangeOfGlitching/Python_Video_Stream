import socket
import time

import pyrealsense2 as rs
import numpy as np
import cv2
from base64 import b64encode
import json

from numpy import uint8

HEADER = 64
PORT = 5050
SERVER = "192.168.50.98"
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECTED"
ADDRESS = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)


def send(msg):
    # b'msg'
    message = msg.encode(FORMAT)
    # 10(string len)
    msg_length = len(message)
    # b'10'
    send_length = str(msg_length).encode(FORMAT)
    # b' ' * (64-2) => b'10                              '
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


prev_frame_time = 0
# used to record the time at which we processed current frame
new_frame_time = 0


# Create a pipeline
pipeline = rs.pipeline()

# Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 2  # 1 meter
clipping_distance = clipping_distance_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

# Streaming loop
try:
    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        # Remove background - Set pixels further than clipping_distance to black

        black_color = 0
        # depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels

        bg_removed_gray = np.where((depth_image > clipping_distance) | (depth_image <= 0), black_color, gray_image)

        # new_frame_time = time.time()
        # fps = 1 / (new_frame_time - prev_frame_time)
        # prev_frame_time = new_frame_time
        # cv2.putText(bg_removed_gray, f"fps{int(fps)}", (7, 70), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
        ##########################################################################################################################################################
        # mix bg_removed_gray and depth_image but need 3_dim shape so put a zero matrix
        # bg_removed_gray_depth shape is 640 * 480 * 3
        # bg_removed_gray is bg_removed_gray_depth[:, :, 0]
        # depth_image is bg_removed_gray_depth[:, :, 1]
        # bg_removed_gray_depth = np.stack((bg_removed_gray, np.uint8(depth_image), np.uint8(depth_image)),
        #                                  axis=2)
        # depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        bg_removed_gray_depth = np.append(bg_removed_gray, depth_image, axis=0)
        # _, JPEG = cv2.imencode(".jpg", bg_removed_gray_depth, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        _, JPEG = cv2.imencode(".jpg", bg_removed_gray_depth, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        JPEG.tofile('DEBUG-original.jpg')
        b64 = b64encode(JPEG)
        message = {"image": b64.decode("utf-8")}
        messageJSON = json.dumps(message)

        send(messageJSON)
        # Render images:
        #   depth align to color on left
        #   depth on right
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # images = np.hstack((bg_removed, depth_colormap))

        # cv2.namedWindow('Align Example', cv2.WINDOW_NORMAL)

        # cv2.imshow('JPEG', JPEG)
        #
        # key = cv2.waitKey(1)
        # # Press esc or 'q' to close the image window
        # if key & 0xFF == ord('q') or key == 27:
        #     cv2.destroyAllWindows()
        #     break
finally:
    pipeline.stop()
