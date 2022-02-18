import json
import numpy as np
import socket
import threading
from base64 import b64decode

import cv2

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECTED"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def stream(frame):
    cv2.imshow("img", frame)
    key = cv2.waitKey(1)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION]{addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            print(f"msg_length {msg_length}")
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            len_msg = len(msg)
            if msg_length != len_msg:
                while int(msg_length) != int(len_msg):
                    msg += conn.recv(msg_length).decode(FORMAT)
                    len_msg = len(msg)
            if msg == DISCONNECT_MSG:
                connected = False
            b64_r = json.loads(msg)
            print(b64_r)
            JPEG_r = b64decode(b64_r["image"])
            frame = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
            stream(frame)

    conn.close()


def start():
    server.listen()
    `(f"[LISTENING] server is listing on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVATE CONNECTING]{threading.active_count() - 1}")


print("[STSRTING] is starting")
start()
