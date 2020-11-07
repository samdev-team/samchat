from tkinter import *
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
        self.root.title('ALTERA CHAT CLIENT V.0.3')
        self.root.resizable(0, 0)
        self.root.config(bg='black')
        self.running = True
        self.listbox = Listbox(self.root, font=('Consolas', 15, 'bold'), bg='black', fg='white', width=52)
        threading.Thread(target=lambda: asyncio.run(self.join())).start()
        self.root.mainloop()

    def exit(self):
        self.running = False
        sys.exit()

    async def join(self):
        con = Label(self.root, text='Connecting', font=('Consolas', 15, 'bold'), bg='black', fg='white')
        con.pack()
        status = await self.connect()
        con.destroy()
        if status:
            label = Label(self.root, text='Connected to server', font=('Consolas', 15, 'bold'), bg='black', fg='white')
            label.pack()
            await asyncio.sleep(1)
            label.destroy()
        else:
            Label(self.root, text='Sorry could not connect to server\nplease try agin later',
                  font=('Consolas', 15, 'bold'), bg='black', fg='white').pack()
            return

        def send_un(event):
            self.sock.send(username.get().encode('utf-8'))
            username.destroy()
            self.root.unbind('<Return>')
            self.Main()

        username = Entry(self.root, font=('Consolas', 15, 'bold'), bg='black', fg='white', insertbackground='white')
        username.pack(side=TOP)
        self.root.bind('<Return>', func=send_un)

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

    def Main(self):
        self.chat_verlabel = Label(text='ALTERA CHAT CLIENT V.0.3', font=('Consolas', 15, 'bold'), bg='black', fg='white')
        self.chat_verlabel.place(x=0, y=0)
        self.listbox.place(x=12, y=50)
        self.message_label = Label(self.root, bg='black', fg='white', text='Message:', font=('Consolas', 15, 'bold'))
        self.message_label.place(x=0, y=320)
        self.msg_input = Text(self.root, bg='black', fg='white', height=1, font=('Consolas', 15, 'bold'),
                          insertbackground='white', bd=3)
        self.msg_input.place(x=0, y=369)
        self.root.bind('<Return>', func=self.sendmsg)
        recv_thread = threading.Thread(target=self.recv)
        recv_thread.setDaemon(True)
        recv_thread.start()


    def sendmsg(self, event):
        msg = str(self.msg_input.get("1.0", END))
        if msg == '':
            pass
        else:
            self.sock.send(msg.encode('utf-8'))
            self.msg_input.delete('1.0', END)

    def recv(self):
        while self.running:
            try:
                hello = self.sock.recv(1024).decode('utf-8')
                self.listbox.insert(0, hello)
            except:
                # destroy widgets
                self.chat_verlabel.destroy()
                self.listbox.destroy()
                self.message_label.destroy()
                self.msg_input.destroy()
                Label(self.root, text='Server connection lost\nplease try again later',
                      font=('Consolas', 15, 'bold'), bg='black', fg='white').pack()
                self.running = False


if __name__ == '__main__':
    client = Main()
