import socket
import threading
from tkinter import *
from tkinter import scrolledtext

dev = True
class Receive_Messages(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self, daemon=True)
        self.parent = parent

    def run(self):
        while True:
            message_data = eval(self.parent.socket.recv_message())
            if not message_data['user_id'] == self.parent.client_id:
                self.parent.add_message(message_data['message'])



class Socket:
    def __init__(self, parent):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parent = parent

    def connect(self):
        try:
            if dev:
                self.sock.connect(('localhost', 8888))
            else:
                self.sock.connect(('52.187.66.7', 8888))
        except WindowsError:
            return False
        return True

    def get_messages(self):
        header = eval(self.recv_message())
        messages = []
        for i in range(header['amount_of_message_lists']):
            messages.insert(0, eval(self.recv_message()))
        return messages

    def send(self, message):
        self.sock.send(message.encode('utf-8'))

    # stuff for over classes
    def recv_message(self):
        return self.sock.recv(20971520).decode('utf-8')


class Main(Tk, threading.Thread):
    def __init__(self):
        Tk.__init__(self)
        threading.Thread.__init__(self, daemon=True)
        self.bgcolor = '#2e2d2d'
        self.geometry('800x500')
        self.title('ALTERA CHAT CLIENT V.1.0')
        self.config(bg=self.bgcolor)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        # define important variables
        self.client_id = None
        self.socket = Socket(self)
        self.recieve_messages = Receive_Messages(self)
        # define widgets
        self.connecting_label = Label(self, text="Connecting", bg=self.bgcolor, fg='white', font=('Consolas', 15, 'bold'))
        self.getting_client_data_label = Label(self, text="Getting client data", bg=self.bgcolor, fg='white', font=('Consolas', 15, 'bold'))
        self.connected_label = Label(self, text="Connected to server", bg=self.bgcolor, fg='white', font=('Consolas', 15, 'bold'))
        self.text_area = scrolledtext.ScrolledText(state=DISABLED, bg=self.bgcolor, fg='white', font=('Consolas', 15, 'bold'))
        self.message_send_entry = Entry(self, bg=self.bgcolor, fg='white', font=('Consolas', 15, 'bold'), insertbackground='white')

    def connect(self):
        self.connecting_label.grid(row=0, sticky="NSEW")
        if not self.socket.connect():
            self.connecting_label.destroy()
            self.connected_label.grid_forget()
            Label(self, text="Server not available try again later", bg=self.bgcolor, fg='white', font=('Consolas', 15, 'bold')).grid(row=0, sticky="NSEW")
            return False
        self.connected_label.grid_forget()
        return True

    def send_message(self):
        message = self.message_send_entry.get()
        self.message_send_entry.delete(0, END)
        self.add_message(message)
        self.socket.send(message)

    def add_message(self, message):
        self.text_area.config(state=NORMAL)
        self.text_area.insert(END, f'\n{message}')
        self.text_area.config(state=DISABLED)
        self.text_area.see('end')

    def message_main(self):
        self.text_area.grid(row=0, sticky="NSEW")
        self.message_send_entry.grid(row=1, sticky="NSEW")
        self.message_send_entry.bind('<Return>', lambda event: self.send_message())

    def run(self):
        # Connect to server
        if self.connect():
            # Get client data
            self.getting_client_data_label.grid(row=0, sticky="NSEW")
            self.client_id = self.socket.recv_message()
            message_lists = self.socket.get_messages()
            # add altera thing
            self.text_area.config(state=NORMAL)
            self.text_area.insert(END, f'Beginning of chat\n')
            self.text_area.config(state=DISABLED)
            # add old messages
            for message_list in message_lists:
                for message in message_list:
                    self.add_message(message)
            # remove label
            self.getting_client_data_label.grid_forget()
            # finish
            self.recieve_messages.start()
            self.message_main()


if __name__ == '__main__':
    app = Main()
    app.start()
    app.mainloop()
