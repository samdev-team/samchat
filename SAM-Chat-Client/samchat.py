import socket
import threading
from tkinter import *
from tkinter import ttk

ip = "127.0.0.1"
port = 8812


class StartMenu(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        parent.clear_window()
        self.sock = Socket()
        self.configure(style="one.TFrame")
        self.parent.style.configure('one.TFrame', background=parent.background_colour)

        self.parent.style.configure('two.TLabel', font=('Helvetica', 20), foreground="white",
                                    background=parent.background_colour)
        ttk.Label(self, text="Amongus obungus", anchor="center", style="two.TLabel").grid(row=2, column=1, pady=20)

        self.parent.style.configure('one.TButton', font=('Helvetica', 30), foreground="white",
                                    background="#4f4f4f", borderwidth=0)
        ttk.Button(self, text="Connect", style="one.TButton", padding=10, width=20, command=self.connect).grid(row=3,
                                                                                                               column=1)
        self.username_input = ttk.Entry(self, width=20, font=('Helvetica', 30), justify='center')

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
            print("connected")
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


class Application(Tk):
    def __init__(self):
        Tk.__init__(self)
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

    def clear_window(self):
        _list = self.winfo_children()
        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        for widget in _list:
            if not widget in self.top_ui:
                widget.grid_forget()

    def start_menu(self):
        self._start_menu.grid(column=1, row=1, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def chat_room(self, sock):
        self.clear_window()
        threading.Thread(target=sock.receive_messages, daemon=True).start()


class Socket(socket.socket, threading.Thread):
    def __init__(self):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self, target=self.receive_messages, daemon=True)

    def send_message(self, msg: str):
        encoded_message = len(msg).to_bytes(4, "little") + msg.encode("utf-8")
        self.send(encoded_message)

    def receive_messages(self):
        while True:
            bufflen = int.from_bytes(self.recv(4), "little")
            msg = self.recv(bufflen).decode("utf-8")
            if bufflen:
                print(f"\n{msg}")
            else:
                self.close()
                break


app = Application()
app.start_menu()

app.mainloop()
