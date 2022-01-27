import socket

HEADER = 64
PORT = 5050
SERVER = "192.168.50.182"
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

while True:
    send("hello word1")
    send("hello word2")
    send("hello word3")

