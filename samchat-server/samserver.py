import socket
import threading
import logging
import sys
import random

import cryptography.exceptions
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


class Client:
    def __init__(self, client):
        self.client = client
        self.ip_address = None
        self.connection_type = None


class Room(Client):
    def __init__(self, client):
        Client.__init__(self, client)
        self.roomname = None
        self.roomcode = None
        self.messages = []

    def receive_messages(self):
        while server_running:
            msg = receive_message(self.client, self.ip_address)
            if msg:
                pass
            else:
                break
        self.remove()

    def remove(self):
        self.client.close()

        del rooms[self.roomcode]
        root.debug(f"({self.ip_address}) Room has disconnected from the server")


class User(Client):
    def __init__(self, client):
        Client.__init__(self, client)
        self.username = None

    def receive_messages(self):
        while server_running:
            msg = receive_message(self.client, self.ip_address)
            if not msg:
                break
            else:
                message_headers, message = read_formatted_message(msg, self.username)
                send_to_all(message, self, True)
        self.remove()

    def remove(self):
        self.client.close()
        del users[self.username]
        send_to_all(f"{self.username} has left the chat", self, False)


port = 25469

server_running = True
users = {}
rooms = {}
messages = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_root = None
root.debug("Initialized socket")

if not os.path.isfile("sam.password"):
    password = input("Please enter a password for users to enter in order for them to decrypt messages\n: ")
    open("sam.password", 'w').write(password)
password_provided = open("sam.password", 'r').read()
password = password_provided.encode("utf-8")

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA512(),
    length=32,
    salt=b'salt_',
    iterations=100000,
    backend=default_backend()
)
key = base64.urlsafe_b64encode(kdf.derive(password))
f = Fernet(key)

root.debug(f"Using {password_provided} as the password for the encryption")


def read_formatted_message(message, username):
    message = message.splitlines()
    print(message)
    message_headers = {
        "message_type": message[0],
        "user_or_room": message[1],
        "message_author": message[2],
        "message_recipient": message[3],
    }
    message = ("\n" + " " * len(username) + "  ").join(message[4:])
    return message_headers, message


def send_formatted_message():
    pass


def process_message(message_headers, message):
    pass


def generate_room_code():
    potential_roomcode = random.randint(100, 999)
    if potential_roomcode in rooms.keys():
        return generate_room_code()
    else:
        return str(potential_roomcode)


def encrypt(msg):
    msg = f.encrypt(msg)
    return msg


def decrypt(msg):
    msg = f.decrypt(msg)
    return msg.decode('utf-8', 'ignore')


def receive_message(client: socket.socket, address):
    try:
        bufflen = int.from_bytes(client.recv(4), "little")
        data = b''
        while True:
            data_part = client.recv(bufflen)
            data += data_part
            if len(data_part) == bufflen:
                break
            else:
                bufflen -= len(data_part)
        if data:
            try:
                data = decrypt(data)
                return data
            except cryptography.fernet.InvalidToken:
                root.debug(f"({address}) client attempted to send a message with the wrong password")
        raise socket.error
    except socket.error or ConnectionResetError:
        root.debug(f"({address}) Stopped receiving data from client")


def send_message(msg, client: socket.socket):
    msg = encrypt(msg.encode('utf-8'))
    encoded_message = len(msg).to_bytes(4, "little") + msg
    client.send(encoded_message)


def send_to_all(msg, user: User, send_username: bool):
    if send_username:
        msg = f"{user.username}: " + msg
    messages.insert(0, msg)
    root.info(f"({user.ip_address}) {msg}")
    for user in users.values():
        send_message(msg, user.client)


def send_previous_messages(user: User):
    root.debug(f"({user.ip_address}) Sending previous messages to user")
    messages_to_send = []
    for message in messages:
        messages_to_send.insert(0, message)

    for message in messages_to_send:
        send_message(message, user.client)


def get_username(user: User):
    username = receive_message(user.client, user.ip_address)
    if username in users.keys():
        send_message("username_exists", user.client)
        return get_username(user)
    else:
        send_message("username_ok", user.client)
        return username


def add_client(client: socket.socket, address):
    user = User(client)
    user.ip_address = address[0]
    root.debug(f"({user.ip_address}) Waiting for username to be sent")
    username = get_username(user)
    if username:
        root.debug(f"({user.ip_address}) Received username {username}")
        user.username = username
        users[username] = user
        root.debug(f"({user.ip_address}) Added user to current connections")
        send_previous_messages(user)
        root.debug(f"({user.ip_address}) Sent messages")
        root.debug(f"({user.ip_address}) User is ready to connect to the chat room")
        send_to_all(f"{username} has connected to the chat", user, False)
        user.receive_messages()


def add_room(client: socket.socket, address):
    room = Room(client)
    room.ip_address = address[0]
    root.debug(f"({room.ip_address}) Waiting for roomname to be sent")
    roomname = receive_message(room.client, room.ip_address)
    if roomname:
        root.debug(f"({room.ip_address}) Received roomname {roomname}")
        room.roomname = roomname
        room.roomcode = generate_room_code()
        rooms[room.roomcode] = room
        send_message(room.roomcode, room.client)
        root.debug("Sent roomcode to dedicated room")


def connection_listener():
    sock.listen()
    root.info("Listening for connections")

    while server_running:
        try:
            conn, addr = sock.accept()
            root.info(f"New connection from {addr[0]}")
            connection_type = receive_message(conn, addr)
            if connection_type == "user":
                root.debug(f"{addr[0]} is a user connection type")
                threading.Thread(target=lambda: add_client(conn, addr), daemon=True).start()
            elif connection_type == "room":
                root.debug(f"{addr[0]} is a room connection type")
                threading.Thread(target=lambda: add_room(conn, addr), daemon=True).start()
            else:
                if connection_type:
                    root.error(f"({addr[0]}) Incorrect connection type")
        except KeyboardInterrupt:
            root.info("Server shutting down")
            root.debug("Closing all connections with users")
            for user in users.values():
                user.client.close()
            root.debug("Closing all connections with rooms")
            for room in rooms.values():
                room.client.close()
            root.info("Server shutdown complete, bye :)")
            exit(0)


sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.bind(("", port))
    root.debug(f"Binded socket to every network interface on port {port}")
    root.debug("Creating server root user")
    server_root = User(None)
    server_root.username = "server"
    server_root.userid = 0
    server_root.ip_address = "sus.sus.sus.sus"

    connection_listener()
except socket.error as e:
    root.error(e)
