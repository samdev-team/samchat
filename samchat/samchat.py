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
from tkinter import *
from tkinter import ttk
import sys
import os

from utilities.samsocket import message, samsocket, Encryption
import utilities.exceptions
import pyaudio

import time

# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 2
# RATE = 44100
# RECORD_TIME = 1
#
# p = pyaudio.PyAudio()
#
# stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=RATE,
#                 input=True,
#                 frames_per_buffer=CHUNK)
#
# stream1 = p.open(format=FORMAT,
#                  channels=CHANNELS,
#                  rate=RATE,
#                  output=True,
#                  frames_per_buffer=CHUNK)

ip = "rozzanet.ddns.net"
port = 25469
version = "7"

if "dev" in sys.argv:
    print("Starting in dev mode")
    ip = "127.0.0.1"


class StartMenu(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
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
            self.parent.sock = samsocket.create_socket()
            self.parent.sock.connect((ip, port))
            self.user_creation()
        except socket.error:
            self.connecting_label.configure(text="Failed to connected (ip doxxed)\ntry again later", justify=CENTER)

    def user_creation(self, exists=False):
        self.clear_window()
        self.parent.unbind("<Return>")
        self.grid_rowconfigure(2, weight=0)
        username_label = ttk.Label(self, text="Zam is zexy", style="three.TLabel", justify=CENTER)

        if exists:
            username_label.configure(text="Username already exists\nEnter a username")
            self.parent.bind("<Return>", self.send_user_data)
            self.username_input.grid(column=1, row=2)
            username_label.grid(column=1, row=1, pady=15)
        else:
            username_label.grid(column=1, row=1, pady=15)
            if not os.path.isfile("sam.password"):
                username_label.configure(text="Enter the password")
                self.username_input.grid(column=1, row=2)
                self.parent.bind("<Return>", self.set_password)
            else:
                if not exists:
                    with open("sam.password", 'r') as file:
                        self.parent.encryption = Encryption(file.read().encode("utf-8", errors="ignore"))
                    samsocket.send_message(self.parent.sock, self.parent.encryption, "user")
                    samsocket.send_message(self.parent.sock, self.parent.encryption, version)
                    try:
                        confirmation = samsocket.receive_message(self.parent.sock,
                                                                 self.parent.encryption).decode("utf-8",
                                                                                                errors="ignore")
                        if confirmation == "old_version_client":
                            username_label.configure(text="You are running an older version of SAM-Chat\n"
                                                          "Please download the latest version at\n"
                                                          "github.com/blockbuster-exe/SAM-Chat")
                            self.parent.sock.close()
                        elif confirmation == "old_version_server":
                            username_label.configure(text="The server is running an older version\n"
                                                          "of SAM-Chat. Please wait until the\n"
                                                          "server maintainers update\n"
                                                          "the server to the latest version")
                            self.parent.sock.close()
                        elif confirmation == "version_good":
                            username_label.configure(text="Enter a username")
                            self.username_input.grid(column=1, row=2)
                            self.parent.bind("<Return>", self.send_user_data)
                    except utilities.exceptions.StreamTerminated:
                        username_label.configure(text=f"Either the server went offline or\n"
                                                      f"you have used the wrong password when \n"
                                                      f"connecting to the server ({ip}).\n\n"
                                                      f" it is highly likely that the password you\n"
                                                      f"entered is wrong please check again with the \n"
                                                      f"server owner")

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
            samsocket.send_message(self.parent.sock, self.parent.encryption, self.username)
            status = samsocket.receive_message(self.parent.sock, self.parent.encryption).decode("utf-8",
                                                                                                errors="ignore")
            if status == "username_exists":
                self.user_creation(True)
            else:
                self.parent.chat_room()

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
        self.samrooms[roomcode] = [f"Beginning of samroom {roomcode}"]

    def change_samroom(self, roomcode):
        if not self.samrooms[roomcode]:
            print(self.samrooms)
            self.add_message("\nYou arnt in that samroom silly\n")
        else:
            self.current_samroom = roomcode
            self.text.configure(state=NORMAL)
            self.text.delete('1.0', END)
            for i in range(100):
                self.text.insert(END, "\n")
            self.text.configure(state=DISABLED)
            self.text.yview_moveto(1)

            self.message_entry.configure(state=DISABLED)
            for message in self.samrooms.get(roomcode):
                self.add_message(message)
            self.message_entry.configure(state=NORMAL)

    def add_room_message(self, message_headers, message):
        self.samrooms[message_headers["recipient"]].append(message)
        if message_headers["recipient"] == self.current_samroom:
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
            samsocket.send_message(self.parent.sock, self.parent.encryption,
                                   message.create_formatted_message('0', self.username, self.current_samroom,
                                                                    msg.encode()).decode("utf-8", errors="ignore"))
            self.add_message(f"{self.username}: {msg}")

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
        self.encryption = None
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

    def chat_room(self):
        self.clear_window()
        self.username_label.configure(text=f"You are logged in as")
        self.username_label1.configure(text=self._start_menu.username)
        self._chat_room.username = self._start_menu.username
        self._chat_room.grid(column=1, row=1, sticky="nsew")
        self._chat_room.create_chat_room()
        threading.Thread(target=receive_messages, daemon=True).start()
        # threading.Thread(target=send_audio_data, daemon=True).start()


# def send_audio_data():
#     while True:
#         data = stream.read(CHUNK)
#         try:
#             samsocket.send_data(app.sock, app.encryption,
#                                 message.create_formatted_message('2', app._start_menu.username, 'server', data))
#         except utilities.exceptions.StreamTerminated:
#             stream.stop_stream()
#             stream.close()
#             stream1.stop_stream()
#             stream1.close()
#             p.terminate()
#             break


def receive_messages():
    while True:
        try:
            formatted_msg = message.read_formatted_message(samsocket.receive_message(app.sock, app.encryption))
            if message:
                if formatted_msg[0]["recipient"] == app._start_menu.username:
                    app._chat_room.add_message(f"{message}")
                else:
                    # if formatted_msg[0]["type"] == "2":
                    #     print("s")
                    #     stream1.write(formatted_msg[1])
                    app._chat_room.add_room_message(formatted_msg[0], formatted_msg[1])
            else:
                break
        except utilities.exceptions.StreamTerminated:
            break
        except utilities.exceptions.EncryptionFailed:
            print("You must have the wrong key dude or thewre is a new bug :DEATH:")
    app.clear_window()
    ttk.Label(app, text="Lost connection with the server\nServer is probably down by "
                        "accident", justify=CENTER, style="three.TLabel").grid(column=1, row=1)
    app.username_label.place_forget()
    app.username_label1.place_forget()


app = Application()
app.start_menu()

app.mainloop()
