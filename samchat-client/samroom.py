import socket
import threading
import cryptography.exceptions
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class Socket(socket.socket, threading.Thread):
    def __init__(self):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self, target=self.receive_messages, daemon=True)

        # encryption
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'salt_',
            iterations=100000,
            backend=default_backend()
        )

    def create_encryption(self):
        password_provided = open("sam.password", 'r').read()
        password = password_provided.encode("utf-8")
        key = base64.urlsafe_b64encode(self.kdf.derive(password))
        self.f = Fernet(key)

    def encrypt(self, msg):
        msg = msg.encode("utf-8", "ignore")
        msg = self.f.encrypt(msg)
        return msg

    def decrypt(self, msg):
        msg = self.f.decrypt(msg)
        return msg.decode('utf-8', 'ignore')

    def send_message(self, msg: str):
        msg = self.encrypt(msg)
        encoded_message = len(msg).to_bytes(4, "little") + msg
        self.send(encoded_message)

    def receive_message(self):
        try:
            bufflen_bytes = self.recv(4)
            bufflen = int.from_bytes(bufflen_bytes, "little")
            data = self.recv(bufflen)
            if data:
                data = self.decrypt(data)
                return data
        except socket.error as e:
            pass

    def receive_messages(self):
        while True:
            msg = self.receive_message()
            if msg:
                self.send_message(msg)
            else:
                self.close()
                break



sock = Socket()

sock.create_encryption()

sock.connect(("127.0.0.1", 25469))

sock.send_message("room")

roomname = input("What is the room name?\n: ")

sock.send_message(roomname)

roomcode = sock.receive_message()

print(roomcode)

while True:
    sock.receive_message()
