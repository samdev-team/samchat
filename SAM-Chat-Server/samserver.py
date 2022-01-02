import socket
import threading
import logging
import sys
import random
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

# logging setup
root = logging.getLogger("SAM-Server")
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


class User:
    def __init__(self, client):
        self.client = client
        self.username = None
        self.userid = None
        self.ip_address = None

    def receive_messages(self):
        while server_running:
            msg = receive_data(self)
            if not msg:
                break
            else:
                send_to_all(msg, self, True)
        self.remove()

    def remove(self):
        self.client.close()
        users.remove(self)
        send_to_all(f"{self.username} has left the chat", self, False)


ip = ""
port = 25469

if "dev" in sys.argv:
    ip = "127.0.0.1"

server_running = True
users = []
messages = ["SAM-Chat -- LOl"]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_root = None
root.debug("Initialized socket")

if not os.path.isfile("sam.password"):
    password = input("Please enter a password for users to enter in order for them to decrypt messages\n: ")
    open("sam.password", 'w').write(password)
password_provided = open("sam.password", 'r').read()
password = password_provided.encode("utf-8")

salt = b'salt_'
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = base64.urlsafe_b64encode(kdf.derive(password))
f = Fernet(key)

root.debug(f"Using {password_provided} as the password for the encryption")


def encrypt(msg):
    msg = f.encrypt(msg)
    return msg


def decrypt(msg):
    msg = f.decrypt(msg)
    return msg.decode('utf-8', 'ignore')


def assign_id():
    userid = random.randint(100, 999)
    for user in users:
        if user.userid == userid:
            assign_id()
    return userid


def receive_data(user: User):
    try:
        bufflen = int.from_bytes(user.client.recv(4), "little")
        data = user.client.recv(bufflen)
        if data:
            data = decrypt(data)
        return data
    except socket.error as e:
        root.error(e)


def send_message(msg, user: User):
    msg = encrypt(msg.encode('utf-8'))
    encoded_message = len(msg).to_bytes(4, "little") + msg
    user.client.send(encoded_message)


def send_to_all(msg, user: User, send_username: bool):
    if send_username:
        msg = f"{user.username}: " + msg
    messages.append(msg)
    root.info(f"({user.userid} | {user.ip_address}) {msg}")
    msg = encrypt(msg.encode('utf-8', 'ignore'))
    encoded_message = len(msg).to_bytes(4, "little") + msg
    for user in users:
        user.client.send(encoded_message)


def send_previous_messages(user: User):
    amount_of_messages = len(messages)
    send_message(str(amount_of_messages), user)
    root.debug(f"({user.userid} | {user.ip_address}) Sending previous messages to user")
    for message in messages:
        send_message(message, user)


def add_client(client: socket.socket, address):
    user = User(client)
    user.userid = assign_id()
    user.ip_address = address[0]
    root.debug(f"Assigned new userid for new connection: {user.userid}")
    root.debug(f"({user.userid} | {user.ip_address}) Waiting for username to be sent")
    username = receive_data(user)
    root.debug(f"({user.userid} | {user.ip_address}) Received username {username}")
    if username:
        user.username = username
        users.append(user)
        root.debug(f"({user.userid} | {user.ip_address}) Added user to current connections")
        send_previous_messages(user)
        root.debug(f"({user.userid} | {user.ip_address}) Sent messages")
        root.debug(f"({user.userid} | {user.ip_address}) User is ready to connect to the chat room")
        send_to_all(f"{username} has connected to the chat", user, False)
        user.receive_messages()


def connection_listener():
    sock.listen()
    root.debug("Listening for connections")

    while server_running:
        conn, addr = sock.accept()
        root.info(f"New connection from {addr[0]}")
        threading.Thread(target=lambda: add_client(conn, addr), daemon=True).start()


try:
    sock.bind((ip, port))
    if ip == "":
        ip = "every network interface"
    root.debug(f"Binded socket to {ip} on port {port}")
    root.debug("Creating server root user")
    server_root = User(None)
    server_root.username = "Server"
    server_root.userid = 0
    server_root.ip_address = "sus.sus.sus.sus"

    connection_listener()
except socket.error as e:
    root.error(e)
