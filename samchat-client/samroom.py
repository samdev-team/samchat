# SAM-Chat is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# SAM-Chat is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with this
# program. If not, see <https://www.gnu.org/licenses/>.


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
            algorithm=hashes.SHA512(),
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


    def send_formatted_message(self, message_type, username, recipient, message):
        msg = f"{message_type}\n" \
              f"{username}\n" \
              f"{recipient}\n" \
              f"{message}"
        self.send_message(msg)

    def send_message(self, msg: str):
        msg = self.encrypt(msg)
        encoded_message = len(msg).to_bytes(4, "little") + msg
        self.send(encoded_message)

    def read_formatted_message(self, formatted_message):
        formatted_message = formatted_message.splitlines()
        message_headers = {
            "message_type": formatted_message[0],
            "message_author": formatted_message[1],
            "message_recipient": formatted_message[2]
        }
        message = "".join(formatted_message[3:])
        if message.startswith("!"):
            message = message[1:]
        else:
            message = f"{message_headers['message_author']}: {message}"
        print(message_headers, message)
        return message_headers, message

    def receive_message(self):
        try:
            bufflen = int.from_bytes(self.recv(4), "little")
            data = b''
            while True:
                data_part = self.recv(bufflen)
                data += data_part
                if len(data_part) == bufflen:
                    break
                else:
                    bufflen -= len(data_part)
            if data:
                data = self.decrypt(data)
                return data
            else:
                self.close()
        except socket.error as e:
            print(e)

    def receive_messages(self):
        while True:
            message = self.receive_message()
            if message:
                messages.append(message)
                print(messages)
            else:
                break


sock = Socket()

sock.create_encryption()

sock.connect(("127.0.0.1", 25469))

sock.send_message("room")

roomname = input("What is the room name?\n: ")

sock.send_message(roomname)

roomcode = sock.receive_message()

print(roomcode)

messages = []

while True:
    sock.receive_messages()
