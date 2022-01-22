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
import logging

from cryptography.fernet import Fernet, InvalidToken
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import socket
import os

import utilities.exceptions


class message:
    @staticmethod
    def read_formatted_message(msg: bytes):
        formatted_msg = msg.splitlines()
        msg_headers = {
            "type": formatted_msg[0].decode("utf-8", errors="ignore"),
            "author": formatted_msg[1].decode("utf-8", errors="ignore"),
            "recipient": formatted_msg[2].decode("utf-8", errors="ignore")
        }
        if msg_headers["type"] == "0" or "1":
            messages = []
            for msg in formatted_msg[3:]:
                messages.append(msg.decode("utf-8", errors="ignore"))
            msg = "\n".join(messages)
        elif msg_headers["type"] == "2" or "3" or "4":
            msg = formatted_msg[3:]
        return [msg_headers, msg]

    @staticmethod
    def create_formatted_message(type_: str, author: str, recipient: str, msg: bytes):
        return f"{type_}\n" \
               f"{author}\n" \
               f"{recipient}\n".encode("utf-8", errors="ignore") \
               + msg


class Encryption(Fernet):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA512(), length=32, salt=b'amougussexylovmao',
                     iterations=100000, backend=default_backend())

    def __init__(self, password):
        # create key
        key = base64.urlsafe_b64encode(self.kdf.derive(password))
        Fernet.__init__(self, key)

    def encrypt_message(self, msg: bytes):
        return self.encrypt(msg)

    def decrypt_message(self, msg: bytes):
        return self.decrypt(msg)


class samsocket:
    @staticmethod
    def create_socket():
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def send_message(sock: socket.socket, encryption: Encryption, msg: str):
        if not encryption:
            print("SAM-Chat does not allow messages to be sent without encryption")
        else:
            msg = encryption.encrypt_message(msg.encode("utf-8", errors="ignore"))
            sock.send(len(msg).to_bytes(4, "little") + msg)

    @staticmethod
    def send_data(sock: socket.socket, encryption: Encryption, data: bytes):
        if not encryption:
            print("SAM-Chat does not allow messages to be sent without encryption")
        else:
            data = encryption.encrypt_message(data)
            sock.send(len(data).to_bytes(4, "little") + data)

    @staticmethod
    def receive_message(sock: socket.socket, encryption: Encryption, ip_address=None, logger=None):
        if not encryption:
            print("SAM-Chat does not allow messages to be received without encryption")
        if not ip_address:
            ip_address = "client"
        try:
            buffer_length = int.from_bytes(sock.recv(4), "little")
            if not buffer_length:
                raise socket.error()
            data = b''
            data_part = 0
            while not data_part == buffer_length:
                data_part = sock.recv(buffer_length)
                data += data_part
                data_part = len(data_part)
                buffer_length -= data_part
            try:
                return encryption.decrypt_message(data)
            except InvalidToken as e:
                if logger:
                    logger.debug(f"({ip_address}) Failed to decrypt message")
                    return None
                else:
                    raise utilities.exceptions.EncryptionFailed(f"({ip_address}) Failed to decrypt message")
        except socket.error or ConnectionResetError as e:
            if logger:
                logger.debug(f"({ip_address}) Socket stream has been terminated")
                return None
            else:
                raise utilities.exceptions.StreamTerminated(f"({ip_address}) Stream has been terminated")
