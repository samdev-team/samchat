# This file is part of SAM-Chat
#
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
import logging
import sys
import random
import time
import os

from utilities.samsocket import samsocket, message, Encryption

# logging setup
root = logging.getLogger("SAM-Server")
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

print("<SAM-Chat Copyright (C) 2022 blockbuster-exe>")


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

    def receive_messages(self):
        while server_running:
            try:
                formatted_msg = message.read_formatted_message(samsocket.receive_message(self.client, encryption,
                                                                                         self.ip_address))
            except:
                break
            if message:
                process_message(formatted_msg, self)
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
            msg = samsocket.receive_message(self.client, encryption, self.ip_address, root)
            if msg:
                formatted_message = message.read_formatted_message(msg)
                process_message(formatted_message, self)
            else:
                break
        self.remove()

    def remove(self):
        self.client.close()
        del users[self.username]
        msg = f"!{self.username} has left the chat"
        if msg.startswith("!"):
            msg = msg[1:]
        else:
            msg = f"{self.username}: {msg}"
        messages.insert(0, [self.username, msg])
        send_to_all(message.create_formatted_message(
            '0', self.username, "server", msg.encode("utf-8", errors="ignore")).decode("utf-8",
                                                                                       errors="ignore"), msg, self,
                    False)


port = 25469

version = 6

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

encryption = Encryption(password)

root.debug(f"Using {password_provided} as the password for the encryption")


def process_message(formatted_msg, room_user):
    if formatted_msg[0]["type"] == '0':
        if isinstance(room_user, User):
            user = room_user
            if formatted_msg[0]['recipient'] == "server":
                if formatted_msg[1].startswith("!"):
                    msg = formatted_msg[1][1:]
                else:
                    msg = f"{user.username}: {formatted_msg[1]}"
                messages.insert(0, [user.username, msg])
                send_to_all(message.create_formatted_message(
                    '0', user.username, "server", msg.encode("utf-8", errors="ignore")).decode("utf-8",
                                                                                               errors="ignore"), msg,
                            user, False)
    #         else:
    #             if message_headers["message_recipient"] in rooms.keys():
    #                 room = rooms[message_headers["message_recipient"]]
    #                 send_message(message.create_formatted_message('0', user.username, None, msg), room.client)
    #     elif isinstance(room_user, Room):
    #         room = room_user
    #         username = message_headers["message_recipient"]
    #         user = users.get(username)
    #         if room.roomcode == message_headers["message_author"]:
    #             if msg.startswith("!"):
    #                 msg = msg[1:]
    #             else:
    #                 msg = f"{user.username}: {msg}"
    #             send_message(create_formatted_message(
    #                 message_type='0', message_author=room.roomcode,
    #                 message_recipient=username, message=msg), user.client)
    #         else:
    #             send_message(create_formatted_message(
    #                 message_type='0', message_author=message_headers["message_author"],
    #                 message_recipient=room.roomcode, message=msg),
    #                 user.client)
    #
    # elif message_headers["message_type"] == '1':
    #     msg = msg.split()
    #
    #     if msg[0] == "joinroom":
    #         user = room_user
    #         if not msg[1] == "server":
    #             if msg[1] in rooms.keys():
    #                 room = rooms[msg[1]]
    #                 root.debug(f"({user.ip_address}) {user.username} is joining room {msg[1]} ({room.roomname})")
    #                 send_message(
    #                     create_formatted_message(message_type="1", message_author="server", message_recipient=None,
    #                                              message=f"adduser {user.username}"), room.client)
    #             else:
    #                 send_message(create_formatted_message(
    #                     message_type="0", message_author="server",
    #                     message_recipient=user.username,
    #                     message=f"""The room "{msg[1]}" doesn't exist"""), user.client)
    #         else:
    #             send_message(create_formatted_message(message_type="0", message_author="server",
    #                                                   message_recipient=user.username,
    #                                                   message="You cant join the server room"), user.client)
    elif formatted_msg[0]["type"] == '2':
        pass


def generate_room_code():
    potential_roomcode = random.randint(100, 999)
    if potential_roomcode in rooms.keys():
        return generate_room_code()
    else:
        return str(potential_roomcode)


def send_to_all(formatted_message: str, msg: str, user: User, send_author: bool):
    root.info(f"({user.ip_address}) {msg}")
    for _user in users.values():
        if _user.username == user.username and send_author:
            samsocket.send_message(_user.client, encryption, formatted_message)
        elif not _user.username == user.username:
            samsocket.send_message(_user.client, encryption, formatted_message)


def send_voice_to_all(formatted_message: bytes):
    for user in users.values():
        try:
            samsocket.send_data(user.client, encryption, formatted_message)
        except socket.error:
            pass


def send_previous_messages(user: User):
    root.debug(f"({user.ip_address}) Sending previous messages to user")
    messages_to_send = []
    for msg in messages:
        messages_to_send.insert(0, [msg[0], msg[1]])

    for msg in messages_to_send:
        samsocket.send_message(user.client, encryption, message.create_formatted_message(
            '0', msg[0], "server", msg[1].encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore"))


def get_username(user: User):
    username = samsocket.receive_message(user.client, encryption, user.ip_address, root)
    if not username:
        return
    username = username.decode("utf-8", errors="ignore")
    if username in users.keys():
        samsocket.send_message(user.client, encryption, "username_exists")
        return get_username(user)
    else:
        samsocket.send_message(user.client, encryption, "username_ok")
        return username


def add_client(client: socket.socket, address):
    user = User(client)
    user.ip_address = address[0]
    root.debug("Checking client version")
    client_version = samsocket.receive_message(user.client, encryption, user.ip_address, root)
    if not client_version:
        return
    client_version = int(client_version.decode("utf-8", errors="ignore"))
    if client_version < version:
        samsocket.send_message(user.client, encryption, "old_version_client")
        root.debug("Client version is older than server version")
    elif client_version > version:
        samsocket.send_message(user.client, encryption, "old_version_server")
        root.info(f"The current server version {version} is out of date, pull the repo to get the latest server")
    elif client_version == version:
        samsocket.send_message(user.client, encryption, "version_good")
        root.debug("Client version matches server version")
        root.debug(f"({user.ip_address}) Waiting for username to be sent")
        username = get_username(user)
        root.debug(f"({user.ip_address}) Received username {username}")
        user.username = username
        send_previous_messages(user)
        root.debug(f"({user.ip_address}) Sent messages")
        root.debug(f"({user.ip_address}) User is ready to join to the chat room")
        users[username] = user
        root.debug(f"({user.ip_address}) Added user to current connections")
        msg = f"!{username} has connected to the chat"
        # send a welcome message to the server room
        if msg.startswith("!"):
            msg = msg[1:]
        else:
            msg = f"{user.username}: {msg}"
        messages.insert(0, [user.username, msg])
        send_to_all(
            message.create_formatted_message(
                '0', user.username, "server",
                msg.encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore"), msg, user, True)
        user.receive_messages()
    else:
        return


def add_room(client: socket.socket, address):
    room = Room(client)
    room.ip_address = address[0]
    root.debug(f"({room.ip_address}) Waiting for roomname to be sent")
    roomname = samsocket.receive_message(room.client, encryption, room.ip_address, root)
    if roomname:
        root.debug(f"({room.ip_address}) Received roomname {roomname}")
        room.roomname = roomname
        room.roomcode = generate_room_code()
        rooms[room.roomcode] = room
        samsocket.send_message(room.client, encryption, room.roomcode)
        root.debug("Sent roomcode to dedicated samroom")
        room.receive_messages()


def connection_listener():
    sock.listen()
    root.info("Listening for connections")

    while server_running:
        try:
            conn, addr = sock.accept()
            root.info(f"New connection from {addr[0]}")
            connection_type = samsocket.receive_message(conn, encryption, addr[0], root)
            if not connection_type:
                root.debug(f"({addr[0]}) User disconnected")
                conn.close()
            else:
                connection_type = connection_type.decode("utf-8", errors="ignore")
                if connection_type == "user":
                    root.debug(f"{addr[0]} is a user connection type")
                    threading.Thread(target=lambda: add_client(conn, addr), daemon=True).start()
                elif connection_type == "room":
                    root.debug(f"{addr[0]} is a room connection type")
                    threading.Thread(target=lambda: add_room(conn, addr), daemon=True).start()
                else:
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
