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
import tkinter
from tkinter import *
from tkinter import ttk
import sys
import cryptography.exceptions
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import time

ip = "rozzanet.ddns.net"
port = 25469
version = "5"

if "dev" in sys.argv:
    print("Starting in dev mode")
    ip = "127.0.0.1"


class StartMenu(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.sock = Socket(self.parent)
        self.parent.style.configure('one.TFrame', background=self.parent.background_colour)
        self.configure(style="one.TFrame")
        self.username = None

        self.username_input = ttk.Entry(self, width=20, font=('Helvetica', 30), justify='center')

    def create_start_menu(self):
        self.parent.style.configure('two.TLabel', font=('Helvetica', 20), foreground="white",
                                    background=self.parent.background_colour)
        ttk.Label(self, text="Amongus obungus", anchor="center", style="two.TLabel").grid(row=2, column=1, pady=20)

        self.parent.style.configure('one.TButton', font=('Helvetica', 30), foreground="white",
                                    background="#4f4f4f", borderwidth=0)
        ttk.Button(self, text="Connect", style="one.TButton", padding=10, width=20, command=self.connect_menu).grid(
            row=3, column=1)
        self.connecting_label = ttk.Label(self, text="Connecting", style="three.TLabel")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

    def connect_menu(self):
        self.clear_window()
        self.parent.style.configure('three.TLabel', font=('Helvetica', 30), foreground="white",
                                    background=self.parent.background_colour)

        self.connecting_label.grid(row=1, column=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0)

        threading.Thread(target=self.connect, daemon=True).start()

    def connect(self):
        try:
            self.sock.connect((ip, port))
            self.user_creation()
        except socket.error:
            self.connecting_label.configure(text="Failed to connected (ip doxxed)\ntry again later", justify=CENTER)

    def user_creation(self, exists=False):
        self.clear_window()
        self.parent.unbind("<Return>")
        self.grid_rowconfigure(2, weight=0)
        username_label = ttk.Label(self, text="Enter a username", style="three.TLabel", justify=CENTER)

        if exists:
            username_label.configure(text="Username already exists\nEnter a username")

        username_label.grid(column=1, row=1, pady=15)
        self.username_input.grid(column=1, row=2)
        if not os.path.isfile("sam.password"):
            username_label.configure(text="Enter the password")
            self.parent.bind("<Return>", self.set_password)
        else:
            if not exists:
                self.sock.create_encryption()
                self.sock.send_message("user")

                self.sock.send_message(version)
                confirmation = self.sock.receive_message()
                if confirmation == "old_version_client":
                    username_label.configure(text="You are running an older version of SAM-Chat\n"
                                                  "Please download the latest version at\n"
                                                  "github.com/blockbuster-exe/SAM-Chat")
                    self.username_input.grid_forget()
                elif confirmation == "old_version_server":
                    username_label.configure(text="The server is running an older version\n"
                                                  "of SAM-Chat. Please wait until the \n"
                                                  "server maintainers update \nthe server to the latest version")
                    self.username_input.grid_forget()
                elif confirmation == "version_good":
                    self.parent.bind("<Return>", self.send_user_data)

    def set_password(self, event):
        password = self.username_input.get()
        open("sam.password", 'w').write(password)
        self.username_input.delete(0, END)
        self.user_creation()

    def send_user_data(self, event):
        self.username = self.username_input.get()
        if not self.username == "":
            self.parent.unbind("<Return>")
            self.username = self.username.replace(" ", "_")
            self.sock.send_message(self.username)
            status = self.sock.receive_message()
            if status == "username_exists":
                self.user_creation(True)
            else:
                self.parent.chat_room(self.sock)

    def clear_window(self):
        _list = self.winfo_children()
        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        for widget in _list:
            widget.grid_forget()


class ChatRoom(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.username = None
        self.current_samroom = None
        self.samrooms = {}

        self.configure(style="one.TFrame")

        self.text = Text(self, width=70, height=15, font=('Consolas', 16), state=DISABLED,
                         background=self.parent.background_colour, foreground="white", insertbackground='white')
        self.text.configure(state=NORMAL)
        for i in range(100):
            self.text.insert(END, "\n")
        self.text.configure(state=DISABLED)
        self.message_entry = Text(self, font=('Consolas', 16), width=5, height=2,
                                  background=self.parent.background_colour, foreground="white",
                                  insertbackground='white', borderwidth=0, border=2)

    def create_chat_room(self):
        self.message_entry.pack(side=BOTTOM, pady=15, padx=15)
        self.text.pack(side=BOTTOM, padx=15)
        self.text.yview_moveto(1)

        # create default server room
        self.samrooms["server"] = []
        self.current_samroom = "server"
        print(self.current_samroom)
        print(self.samrooms)

        self.parent.bind("<Return>", self.send_message)
        self.parent.bind("<Configure>", self.on_resize)

    def add_samroom(self, roomcode):
        self.samrooms[roomcode] = []
        self.current_samroom = roomcode

    def change_samroom(self, roomcode):
        if not self.samrooms.get(roomcode):
            pass

        self.text.configure(state=NORMAL)
        self.text.delete('1.0', END)
        self.text.configure(state=DISABLED)
        self.text.yview_moveto(1)

        for message in self.samrooms.get(roomcode):
            self.add_message(message)

    def add_room_message(self, message_headers, message):
        self.samrooms[message_headers["message_recipient"]].append(message)
        if message_headers["message_recipient"] == self.current_samroom:
            self.add_message(message)

    def add_message(self, message):
        self.text.configure(state=NORMAL)
        self.text.insert(END, f"\n{message}")
        self.text.configure(state=DISABLED)
        self.text.yview_moveto(1)

    def send_message(self, event):
        msg = self.message_entry.get(1.0, END)
        msg = msg.rstrip("\n")
        self.message_entry.delete('1.0', END)
        if msg.startswith("!"):
            self.parent.sock.process_command(msg)
        elif not msg == "":
            self.parent.sock.send_formatted_message('0', self.username, self.current_samroom, msg)
            # self.add_message(f"{self.username}: {msg}")

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.configure(width=event.width)
        self.text.configure(height=event.height, width=event.width)
        self.message_entry.configure(width=event.width)
        self.text.yview_moveto(1)

    def clear_window(self):
        _list = self.winfo_children()
        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        for widget in _list:
            widget.pack_forget()


class Application(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.sock = None
        self.background_colour = "#2d2d2d"
        self.title("SAM-Chat")
        self.geometry("900x600")
        self.configure(background=self.background_colour)
        self.style = ttk.Style(self)

        self.top_ui = []

        self.style.configure('one.TLabel', font=('Helvetica', 40, 'bold'), foreground="white",
                             background=self.background_colour)
        self.top_label = ttk.Label(self, text="SAM-Chat", anchor="center", style="one.TLabel")
        self.top_label.grid(row=0, column=1, sticky="nsew", pady=15)
        self.style.configure("four.TLabel", background=self.background_colour, font=('Helvetica', 13, 'bold'))
        self.username_label = ttk.Label(self, text="", style="four.TLabel", foreground="white")
        self.username_label.place(x=15, y=5)
        self.username_label1 = ttk.Label(self, text="", style="four.TLabel", foreground="orange",
                                         font=('Helvetica', 16, 'bold'))
        self.username_label1.place(x=15, y=30)

        self.top_ui.append(self.username_label)
        self.top_ui.append(self.top_label)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self._start_menu = StartMenu(self)
        self._chat_room = ChatRoom(self)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def clear_window(self):
        _list = self.winfo_children()
        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        for widget in _list:
            if not widget in self.top_ui:
                widget.grid_forget()

    def start_menu(self):
        self.clear_window()

        self._start_menu.grid(column=1, row=1, sticky="nsew")
        self._start_menu.create_start_menu()

    def chat_room(self, sock):
        self.clear_window()
        self.username_label.configure(text=f"You are logged in as")
        self.username_label1.configure(text=self._start_menu.username)
        self.sock = sock
        sock.username = self._start_menu.username
        self._chat_room.username = self._start_menu.username
        self._chat_room.grid(column=1, row=1, sticky="nsew")
        self._chat_room.create_chat_room()
        sock.start()


class Socket(socket.socket, threading.Thread):
    def __init__(self, parent):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self, target=self.receive_messages, daemon=True)
        self.parent = parent
        self.username = None
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

    def process_command(self, message):
        message = message[1:].split()
        if message[0] == "fetch":
            if len(message[1:]) == 1:
                self.send_formatted_message(message_type="1", username=self.username, recipient="server",
                                            message=f"fetch {message[1]}")
            else:
                print(f"Too many arguments, expected 1 got {len(message)}")

        if message[0] == "addroom":
            if len(message[1:]) == 1:
                self.send_formatted_message(message_type="1", username=self.username, recipient="server",
                                            message=f"joinroom {message[1]}")
                self.parent._chat_room.add_samroom(message[1])
            else:
                print(f"Too many arguments, expected 1 got {len(message)}")

        if message[0] == "changeroom":
            if len(message[1:]) == 1:
                self.parent._chat_room.change_samroom(message[1])
            else:
                print(f"Too many arguments, expected 1 got {len(message)}")

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
            formatted_message = self.receive_message()
            if formatted_message:
                message_headers, message = self.read_formatted_message(formatted_message)
                if message_headers["message_recipient"] == self.username:
                    self.parent._chat_room.add_message(f"{message}")
                else:
                    self.parent._chat_room.add_room_message(message_headers, message)
            else:
                break
        self.parent.clear_window()
        ttk.Label(text="Lost connection with the server\nServer is probably down by "
                       "accident", justify=CENTER, style="three.TLabel").grid(column=1, row=1)
        self.parent.username_label.place_forget()
        self.parent.username_label1.place_forget()


app = Application()
app.start_menu()

app.mainloop()
