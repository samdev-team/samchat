from tkinter import *
from PIL import Image, ImageTk
import socket
import threading
import asyncio
import os


class Main:
    def __init__(self):
        self.root = Tk()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.geometry('800x500')
        self.root.title('ALTERA CHAT CLIENT V.0.4')
        self.root.resizable(0, 0)
        self.bgcolor = '#2e2d2d'
        img = ImageTk.PhotoImage(Image.open('assets/ALTERA-CHAT-BG.jpg'))
        Label(self.root, image=img).place(x=0, y=0, relwidth=1, relheight=1)
        self.running = True
        self.messages = []
        self.frame = Frame(self.root, bg=self.bgcolor, width=700, height=330)
        threading.Thread(target=lambda: asyncio.run(self.join())).start()
        self.root.mainloop()

    def exit(self):
        self.running = False
        sys.exit()

    async def join(self):
        con = Label(self.root, text='Connecting', font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white')
        con.place(x=340, y=20)
        status = await self.connect()
        con.destroy()
        if status:
            label = Label(self.root, text='Connected to server', font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white')
            label.place(x=300, y=20)
            await asyncio.sleep(1)
            label.destroy()
        else:
            Label(self.root, text='Sorry could not connect to server\nplease try agin later',
                  font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white').place(x=230, y=20)
            return

        def send_un():
            self.sock.send(username.get().encode('utf-8'))
            label.destroy()
            username.destroy()
            self.root.unbind('<Return>')
            self.Main()
        label = Label(self.root, text='Choose a username', font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white')
        label.place(x=310, y=20)
        username = Entry(self.root, font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white', insertbackground='white')
        username.place(x=300, y=50)
        self.root.bind('<Return>', func=lambda event: send_un())

    async def connect(self):
        try:
            try:
                self.sock.connect(('altera-server.ddns.net', 2288))
                return True
            except:
                self.sock.connect(('localhost', 2288))
                return True
        except:
            print('No servers are available')
            return False

    def add_prev_messages(self):
        for msg in self.prev_msg:
            for i in self.messages:
                i['label'].place(x=0, y=i['location'] - 30)
                i['location'] -= 30
            self.messages.append(
                {'label':Label(self.frame, text=msg, font=('Consolas', 15, 'bold'), bg='#4c4c4c', fg='white'),
                 'location':290})
            index = len(self.messages) - 1
            self.messages[index]['label'].place(x=0, y=290)


    def Main(self):
        self.chat_verlabel = Label(text='ALTERA CHAT V.0.4', font=('Consolas', 25, 'bold'), bg=self.bgcolor, fg='white')
        self.chat_verlabel.place(x=25, y=20)
        self.prev_msg = eval(self.sock.recv(1024).decode('utf-8'))
        self.frame.place(x=40, y=80)
        self.add_prev_messages()
        self.message_label = Label(self.root, bg=self.bgcolor, fg='white', text='Message:', font=('Consolas', 15, 'bold'))
        self.message_label.place(x=25, y=420)
        self.msg_input = Text(self.root, bg=self.bgcolor, fg='white', height=1, font=('Consolas', 15, 'bold'),
                          insertbackground='white', bd=3, width=67)
        self.msg_input.place(x=25, y=450)
        self.root.bind('<Return>', func=self.sendmsg)
        recv_thread = threading.Thread(target=lambda: asyncio.run(self.recv()))
        recv_thread.setDaemon(True)
        recv_thread.start()


    def sendmsg(self, event):
        msg = str(self.msg_input.get("1.0", END)).rstrip()
        if msg == '':
            self.msg_input.delete('1.0', END)
            pass
        else:
            self.sock.send(msg.encode('utf-8'))
            self.msg_input.delete('1.0', END)


    async def recv(self):
        while self.running:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                if msg == '':
                    raise Exception('server_disconnected')
                if len(self.messages) == 13:
                    self.messages[0]['label'].destroy()
                    self.messages.remove(self.messages[0])
                for i in self.messages:
                    i['label'].place(x=0, y=i['location']-30)
                    i['location'] -= 30
                self.messages.append({'label': Label(self.frame, text=msg, font=('Consolas', 15, 'bold'), bg='#4c4c4c', fg='white'), 'location': 290})
                index = len(self.messages)-1
                self.messages[index]['label'].place(x=0, y=290)

            except:
                # destroy widgets
                self.chat_verlabel.place(x=-1000, y=-1000)
                self.frame.place(x=-1000, y=-1000)
                self.message_label.place(x=-1000, y=-1000)
                self.msg_input.place(x=-1000, y=-1000)
                Label(self.root, text='Server connection lost\nplease try again later',
                      font=('Consolas', 15, 'bold'), bg=self.bgcolor, fg='white').place(x=230, y=25)
                self.running = False


if __name__ == '__main__':
    client = Main()
