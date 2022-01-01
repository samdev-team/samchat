import socket
import threading
import logging
import sys

# logging setup
root = logging.getLogger("SAM-Server")
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


class User:
    def __init__(self, client: socket.socket):
        self.client = client
        self.username = None

    def receive_messages(self):
        while server_running:
            msg = receive_data(self)
            if not msg:
                break
            else:
                send_to_all(f"{self.username}: {msg}")
        self.remove()

    def remove(self):
        self.client.close()
        users.remove(self)
        send_to_all(f"{self.username} has left the chat")
        root.info(f"{self.username} has disconnected")


ip = "127.0.0.1"
port = 8812

server_running = True
users = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
root.debug("Initialized socket")


def receive_data(user: User):
    bufflen = int.from_bytes(user.client.recv(4), "little")
    data = user.client.recv(bufflen).decode("utf-8")
    return data


def send_to_all(msg):
    root.debug(msg)
    encoded_message = len(msg).to_bytes(4, "little") + msg.encode("utf-8")
    for user in users:
        user.client.send(encoded_message)


def add_client(client: socket.socket):
    user = User(client)
    username = receive_data(user)
    if username:
        user.username = username
        users.append(user)
        send_to_all(f"{username} has connected to the chat")
        user.receive_messages()


def connection_listener():
    sock.listen()
    root.debug("Listening for connections")

    while server_running:
        conn, addr = sock.accept()
        root.info(f"New connection from {addr[0]}")
        threading.Thread(target=lambda: add_client(conn), daemon=True).start()


sock.bind((ip, port))
root.debug(f"Binded socket to {ip} on port {port}")

connection_listener()