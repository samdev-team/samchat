from tkinter import *
from PIL import Image, ImageTk
import socket
import threading
import asyncio
import os


class Main:
    def __init__(self):
        # Tkinter and socket
        self.root = Tk()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.geometry('800x500')
        self.root.title('ALTERA CHAT CLIENT V.0.5')
        self.root.resizable(0, 0)
        # Background data
        self.bgcolor = '#2e2d2d'
        img = ImageTk.PhotoImage(Image.open('assets/ALTERA-CHAT-BG.jpg'))
        Label(self.root, image=img).place(x=0, y=0, relwidth=1, relheight=1)
        # Misc
        self.running = True
        self.messages = []
        # Widgets
        self.frame = Frame(self.root, bg=self.bgcolor, width=600, height=330)
        self.users_list = Listbox(self.root, font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white', width=15,
                                  height=17)
        self.chat_verlabel = Label(text='ALTERA CHAT V.0.5', font=('Consolas', 25, 'bold'), bg=self.bgcolor, fg='white')
        self.message_label = Label(self.root, bg=self.bgcolor, fg='white', text='Message:',
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
        status = await self.connect()
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
            self.sock.send(username.get().encode('utf-8'))
            label.destroy()
            username.destroy()
            self.root.unbind('<Return>')
            await self.Main()

        label = Label(self.root, text='Choose a username', font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white')
        label.place(x=310, y=20)
        username = Entry(self.root, font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white',
                         insertbackground='white')
        username.place(x=300, y=50)
        self.root.bind('<Return>', func=lambda event: asyncio.run(send_un()))

    async def connect(self):
        try:
            try:
                self.sock.connect(('altera-server.ddns.net', 2288))
                return True
            except:
                self.sock.connect(('localhost', 2288))
                return True
        except:
            return False

    async def add_messages(self, msg):
        for i in self.messages:
            i['label'].place(x=0, y=i['location'] - 30)
            i['location'] -= 30
        self.messages.append(
            {'label': Label(self.frame, text=msg, font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white'),
             'location': 280})
        index = len(self.messages) - 1
        self.messages[index]['label'].place(x=0, y=280)

    async def place_widgets(self, set):
        if set == 'main':
            self.chat_verlabel.place(x=25, y=20)
            self.frame.place(x=40, y=80)
            self.message_label.place(x=25, y=420)
            self.msg_input.place(x=25, y=450)
            self.users_list.place(x=600, y=25)

    def recv_msg(self):
        msg = self.sock.recv(1024).decode('utf-8')
        self.sock.send('recv'.encode('utf-8'))
        return msg

    async def Main(self):
        # set up messages and users
        await self.place_widgets('main')
        self.prev_msg = eval(self.recv_msg())
        self.users = eval(self.recv_msg())
        self.users_list.insert(END, 'Users:')
        for name in self.users:
            self.users_list.insert(END, name)
        for msg in self.prev_msg:
            await self.add_messages(msg)
        self.root.bind('<Return>', func=lambda event: asyncio.run(self.sendmsg()))
        threading.Thread(target=lambda: asyncio.run(self.recv()), daemon=True).start()

    async def sendmsg(self):
        msg = str(self.msg_input.get("1.0", END)).rstrip()
        if msg == '':
            self.msg_input.delete('1.0', END)
            pass
        else:
            self.sock.send(msg.encode('utf-8'))
            self.msg_input.delete('1.0', END)

    async def syscmd(self, msg):
        args = msg.split()
        syscmd = args[1]
        all_args = args[2:]
        if syscmd == 'user_joined':
            self.users_list.insert(END, all_args[0])
        if syscmd == 'user_changed_nick':
            old_nick = all_args[0]
            new_nick = all_args[1]
            index = self.users_list.get(0, END).index(old_nick)
            self.users_list.delete(index)
            self.users_list.insert(index, new_nick)

    async def recv(self):
        while self.running:
            try:
                msg = self.recv_msg()
                if msg.startswith('sys_htas2789'):
                    await self.syscmd(msg)
                    pass
                else:
                    if msg == '':
                        raise Exception('server_disconnected')
                    if len(self.messages) == 13:
                        self.messages[0]['label'].destroy()
                        self.messages.remove(self.messages[0])
                    await self.add_messages(msg)

            except WindowsError:
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