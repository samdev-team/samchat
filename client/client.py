from tkinter import *
from PIL import Image, ImageTk
import socket
import threading
import asyncio
import os


class Socket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sys = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    async def connect(self):
        try:
            try:
                raise Exception()
                # self.sock.connect(('localhost', 2288))
                # self.sys.connect(('localhost', 2289))
                # return True
            except:
                self.sock.connect(('localhost', 2288))
                self.sys.connect(('localhost', 2289))
                return True
        except:
            return False

    async def send(self, msg):
        self.sock.send(msg.encode('utf-8'))

    async def recv_sys(self):
        return self.sys.recv(4096).decode('utf-8')

    async def recv_sock(self):
        return self.sock.recv(4096).decode('utf-8')

class Main:
    def __init__(self):
        # Tkinter and socket
        self.root = Tk()
        self.socket = Socket()
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.geometry('800x500')
        self.root.title('ALTERA CHAT CLIENT V.0.5')
        self.root.resizable(0, 0)
        # Background data
        self.bgcolor = '#2e2d2d'
        img = ImageTk.PhotoImage(Image.open('assets/ALTERA-CHAT-BG.jpg'))
        Label(self.root, image=img).place(x=0, y=0, relwidth=1, relheight=1)
        self.running = True
        # Widgets
        self.frame = Text(self.root, bg=self.bgcolor, width=50, height=15, bd=0, font=('Consolas', 15, 'bold'), fg='white')
        self.frame.configure(inactiveselectbackground=self.frame.cget("selectbackground"))
        self.users_list = Listbox(self.root, font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white', width=15,
                                  height=17)
        self.chat_verlabel = Label(text='ALTERA CHAT V.0.5', font=('Consolas', 25, 'bold'), bg=self.bgcolor, fg='white')
        self.message_label = Label(self.root, bg=self.bgcolor, fg='white', text='Message:                                           ',
                                   font=('Consolas', 15, 'bold'))
        self.msg_input = Text(self.root, bg=self.bgcolor, fg='white', height=1, font=('Consolas', 15, 'bold'),
                              insertbackground='white', bd=3, width=67)
        # Start app
        threading.Thread(target=lambda: asyncio.run(self.join())).start()
        self.root.mainloop()

    def exit(self):
        # stop app
        self.running = False
        self.root.destroy()
        sys.exit()

    async def temp_label(self, text):
        return Label(self.root, text=text, font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white')

    async def join(self):
        conlabel = await self.temp_label('Connecting')
        conlabel.place(x=340, y=20)
        status = await self.socket.connect()
        conlabel.destroy()
        if status:
            connectedlabel = await self.temp_label('Connected to server')
            connectedlabel.place(x=300, y=20)
            await asyncio.sleep(1)
            connectedlabel.destroy()
        else:
            Label(self.root, text='Sorry could not connect to server\nplease try agin later',
                  font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white').place(x=230, y=20)
            return

        async def send_un():
            await self.socket.send(self.username.get())
            label.destroy()
            self.root.unbind('<Return>')
            await self.Main()

        label = Label(self.root, text='Choose a username', font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white')
        label.place(x=310, y=20)
        self.username = Entry(self.root, font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white',
                         insertbackground='white')
        self.username.place(x=300, y=50)
        self.root.bind('<Return>', func=lambda event: asyncio.run(send_un()))

    async def add_message(self, msg):
        self.frame.configure(state='normal')
        self.frame.insert(END, f'{msg}\n')
        self.frame.configure(state='disabled')
        self.frame.see('end')


    async def place_widgets(self, set):
        if set == 'main':
            self.chat_verlabel.place(x=25, y=20)
            self.username_label[0].place(x=20, y=455)
            self.username_label[1].place(x=298, y=455)
            self.frame.place(x=40, y=65)
            self.message_label.place(x=25, y=394)
            self.msg_input.place(x=25, y=420)
            # self.users_list.place(x=600, y=25)

    async def Main(self):
        # get username and destroy widget
        username = self.username.get()
        self.username.destroy()
        # set up messages and users
        self.username_label = [Label(self.root, bg=self.bgcolor, fg='white', text=f'You are currently logged in as',
                                   font=('Consolas', 13, 'bold')), Label(self.root, bg=self.bgcolor, fg='orange', text=username,
                                   font=('Consolas', 13, 'bold'))]
        await self.place_widgets('main')
        msg = await self.socket.recv_sys()
        self.prev_msg = eval(msg)
        msg = await self.socket.recv_sys()
        self.users = eval(msg)
        self.users_list.insert(END, 'Users:')
        for name in self.users:
            self.users_list.insert(END, name)
        for msg in self.prev_msg:
            await self.add_message(msg)
        self.root.bind('<Return>', func=lambda event: asyncio.run(self.sendmsg()))
        threading.Thread(target=lambda: asyncio.run(self.recv()), daemon=True).start()
        threading.Thread(target=lambda: asyncio.run(self.sysrecv()), daemon=True).start()

    async def sendmsg(self):
        msg = str(self.msg_input.get("1.0", END)).rstrip()
        if msg == '':
            self.msg_input.delete('1.0', END)
            pass
        else:
            await self.socket.send(msg)
            self.msg_input.delete('1.0', END)

    async def syscmd(self, msg):
        args = msg.split()
        syscmd = args[1]
        all_args = args[2:]
        if syscmd == 'user_joined':
            pass
        if syscmd == 'user_changed_nick':
            old_nick = all_args[0]
            new_nick = all_args[1]
            self.username_label[1].config(text=new_nick)

    async def sysrecv(self):
        while self.running:
            msg = await self.socket.recv_sys()
            await self.syscmd(msg)

    async def recv(self):
        while self.running:
            try:
                msg = await self.socket.recv_sock()
                if msg == '':
                    raise Exception('server_disconnected')
                await self.add_message(msg)

            except WindowsError or Exception:
                # destroy widgets
                self.chat_verlabel.place(x=-1000, y=-1000)
                self.frame.place(x=-1000, y=-1000)
                self.message_label.place(x=-1000, y=-1000)
                self.msg_input.place(x=-1000, y=-1000)
                self.users_list.place(x=-1000, y=-1000)
                Label(self.root, text='Server connection lost\nplease try again later',
                      font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white').place(x=265, y=25)
                self.running = False


if __name__ == '__main__':
    client = Main()
