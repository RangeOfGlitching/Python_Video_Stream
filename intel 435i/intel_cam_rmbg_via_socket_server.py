import numpy as np
import socket
import threading
import sys
from base64 import b64decode
import cv2
import json

#########################################################################
# socket
HEADER = 64
PORT = 5050

SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT_LENGTH = "utf-8"
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECTED"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)


#########################################################################
#########################################################################
# stream_fac_rec
# sfr = SimpleFacerec()
# sfr.load_encoding_images("me/")
#
# process_this_frame = True
#########################################################################


def stream_fac_rec(frame):
    cv2.imshow('stream', frame)
    key = cv2.waitKey(1)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION]{addr} connected.")

    connected = True
    while connected:
        desireMsgLength = conn.recv(HEADER).decode(FORMAT)
        if desireMsgLength:
            desireMsgLength = int(desireMsgLength)
            msg = conn.recv(desireMsgLength).decode(FORMAT)
            realMshLength = len(msg)
            # print(f"msg_length {desireMsgLength}")
            # print(f"    not match {realMshLength}")
            while desireMsgLength > realMshLength:
                remain_data_size = desireMsgLength - realMshLength
                msg_compensation = conn.recv(remain_data_size).decode(FORMAT)
                # print(f"    remain_data_size {remain_data_size}")
                # print(f"msg_compensation [len({len(msg_compensation)}){msg_compensation}]")
                msg += msg_compensation
                realMshLength = len(msg)

                if realMshLength > desireMsgLength:
                    print("overload")
                    print(msg)
                    assert False
            if msg == DISCONNECT_MSG:
                connected = False

            b64_r = json.loads(msg)
            JPEG_r = b64decode(b64_r["image"])
            frame = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            stream_fac_rec(frame)

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] server is listing on {SERVER}")
    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)
        # thread = threading.Thread(target=handle_client, args=(conn, addr)\)
        # thread.start()
        # print(f"[ACTIVATE CONNECTING]{threading.active_count() - 1}")


print("[STSRTING] is starting")
start()
