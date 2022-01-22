import socket
import time
from base64 import b64encode
import cv2
import json
HEADER = 64
PORT = 5050
SERVER = "192.168.50.194"
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECTED"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


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


cap = cv2.VideoCapture(1)
prev_frame_time = 0
# used to record the time at which we processed current frame
new_frame_time = 0

while True:
    # ret is T(got frame) or F
    ret, frame = cap.read()

    # Fps
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    cv2.putText(frame, f"fps{int(fps)}", (7, 70), cv2.FONT_HERSHEY_DUPLEX, 2, (100, 255, 0), 2, cv2.LINE_AA)
    _, JPEG = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    JPEG.tofile('DEBUG-original.jpg')
    b64 = b64encode(JPEG)
    message = {"image": b64.decode("utf-8")}
    messageJSON = json.dumps(message)
    send(messageJSON)
    # cv2.imshow("Stream", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
