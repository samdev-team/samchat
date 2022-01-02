import socket
import threading
from tkinter import *
from tkinter import ttk
import sys
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


ip = "rozzanet.ddns.net"
port = 25469

if "dev" in sys.argv:
    ip = "127.0.0.1"


class StartMenu(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.sock = Socket(self.parent)
        self.parent.style.configure('one.TFrame', background=self.parent.background_colour)
        self.configure(style="one.TFrame")

        self.username_input = ttk.Entry(self, width=20, font=('Helvetica', 30), justify='center')

    def create_start_menu(self):
        self.parent.style.configure('two.TLabel', font=('Helvetica', 20), foreground="white",
                                    background=self.parent.background_colour)
        ttk.Label(self, text="Amongus obungus", anchor="center", style="two.TLabel").grid(row=2, column=1, pady=20)

        self.parent.style.configure('one.TButton', font=('Helvetica', 30), foreground="white",
                                    background="#4f4f4f", borderwidth=0)
        ttk.Button(self, text="Connect", style="one.TButton", padding=10, width=20, command=self.connect).grid(row=3,
                                                                                                               column=1)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

    def connect(self):
        self.clear_window()
        self.parent.style.configure('three.TLabel', font=('Helvetica', 30), foreground="white",
                                    background=self.parent.background_colour)
        connecting_label = ttk.Label(self, text="Connecting", style="three.TLabel")
        connecting_label.grid(row=1, column=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0)

        try:
            self.sock.connect((ip, port))
            self.user_creation()
        except socket.error:
            connecting_label.configure(text="Failed to connected (ip doxxed)\ntry again later")

    def user_creation(self):
        self.clear_window()
        self.grid_rowconfigure(2, weight=0)
        username_label = ttk.Label(self, text="Enter a username", style="three.TLabel")
        username_label.grid(column=1, row=1, pady=15)
        self.username_input.grid(column=1, row=2)
        self.parent.bind("<Return>", self.send_user_data)

    def send_user_data(self, event):
        self.parent.unbind("<Return>")
        username = self.username_input.get()
        no_space_username = username.replace(" ", "_")
        self.sock.send_message(no_space_username)
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

        self.configure(style="one.TFrame")

        self.text = Text(self, width=70, height=15, font=('Consolas', 16), state=DISABLED,
                         background=self.parent.background_colour, foreground="white", insertbackground='white')
        self.message_entry = Text(self, font=('Consolas', 16), width=50, height=2,
                                  background=self.parent.background_colour, foreground="white",
                                  insertbackground='white', borderwidth=0)

    def create_chat_room(self):
        self.message_entry.pack(side=BOTTOM, pady=15, padx=15)
        self.text.pack(side=BOTTOM, padx=15)
        self.text.configure(state=NORMAL)
        for i in range(100):
            self.text.insert(END, "\n")
        self.text.configure(state=DISABLED)
        self.text.yview_moveto(1)

        self.parent.bind("<Return>", self.send_message)
        self.parent.bind("<Configure>", self.on_resize)

    def add_message(self, msg):
        self.text.configure(state=NORMAL)
        self.text.insert(END, f"\n{msg}")
        self.text.configure(state=DISABLED)
        self.text.yview_moveto(1)

    def send_message(self, event):
        msg = self.message_entry.get(1.0, END)
        msg = msg.rstrip("\n")
        self.parent.sock.send_message(msg)
        self.message_entry.delete('1.0', END)

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
            widget.grid_forget()


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
        self.sock = sock
        sock.start()

        self._chat_room.grid(column=1, row=1, sticky="nsew")
        self._chat_room.create_chat_room()


class Socket(socket.socket, threading.Thread):
    def __init__(self, parent):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self, target=self.receive_messages, daemon=True)
        self.parent = parent
        # encryption
        if not os.path.isfile("sam.password"):
            password = input("Please enter the password: ")
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

    def receive_messages(self):
        while True:
            bufflen = int.from_bytes(self.recv(4), "little")
            msg = self.decrypt(self.recv(bufflen))
            if bufflen:
                self.parent._chat_room.add_message(msg)
            else:
                self.close()
                break


app = Application()
app.start_menu()

app.mainloop()