import numpy as np
import socket
import threading
import sys
from base64 import b64decode
import cv2
import json
from simple_facerec import SimpleFacerec

#########################################################################
# socket
HEADER = 64
PORT = 5050

SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECTED"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
#########################################################################
#########################################################################
# stream_fac_rec
sfr = SimpleFacerec()
sfr.load_encoding_images("me/")

process_this_frame = True
#########################################################################


def stream_fac_rec(frame):
    # print("hello")
    bg_gray = frame[:480, :]
    depth = frame[480:, :]

    # if process_this_frame:
    face_locations, face_names = sfr.detect_known_faces(bg_gray)
    for face_loc, face_name in zip(face_locations, face_names):
        # face_loc[ 24 372 168 228]
        # face_loc[ (top right) ( bottom left)]
        x1, y1, x2, y2 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
        # dis = depth[x3, y3]
        cv2.putText(bg_gray, face_name, (y2, x1 - 30), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0),
                    2)

        cv2.rectangle(bg_gray, (y1, x1), (y2, x2), (0, 0, 255), 3)
        cv2.imshow('bg_gray', bg_gray)

    # process_this_frame = not process_this_frame

    key = cv2.waitKey(1)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION]{addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            # print(f"msg_length {msg_length}")
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
            JPEG_r = b64decode(b64_r["image"])
            frame = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            stream_fac_rec(frame)

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] server is listing on {SERVER}")
    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)
        # thread = threading.Thread(target=handle_client, args=(conn, addr))
        # thread.start()
        # print(f"[ACTIVATE CONNECTING]{threading.active_count() - 1}")


print("[STSRTING] is starting")
start()
