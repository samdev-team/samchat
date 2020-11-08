import socket
import asyncio
from threading import Thread
from datetime import datetime
import re


class Main:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.task = None
        self.clients = []
        self.messages = []
        try:
            self.sock.bind(('192.168.0.69', 2288))
        except:
            self.sock.bind(('localhost', 2288))

    async def handle(self):
        self.sock.listen(1)
        print('Main-thread: Listening for connections')
        while True:
            s, a = self.sock.accept()
            print(f'Main-thread: {a[0]} has connected')
            try:
                username = s.recv(1024).decode('utf-8')
                await self.connect(s, username)
            except:
                print(f'Main-thread: {a[0]} has disconnected')

    async def connect(self, s, username):
        self.clients.append({'name':username, 'client':s})
        self.index = len(self.clients) - 1
        s.send(str(self.messages).encode('utf-8'))
        users = []
        for i in self.clients:
            users.append(i['name'])
        s.send(str(users).encode('utf-8'))
        await self.wait_for_check(s)
        Thread(target=lambda:asyncio.run(self.client_thread()), daemon=True).start()
        await self.send(username + " has joined the chat")

    async def wait_for_check(self, s):
        await asyncio.wait_for(s.recv(1024), 100)
        print('done')

    async def disconnect(self, client):
        name = client["name"]
        self.clients.remove(client)
        await self.send(name + " has left the chat")

    async def commands(self, msg, client_data):
        if msg.startswith('.'):
            try:
                args = msg.replace('.', '').split()
                cmd = args[0]
                all_args = args[1:]
                if cmd == 'nick':
                    new_nick = ' '.join(all_args)
                    if new_nick.startswith(''):
                        await self.send('Cant change your nick to that')
                    else:
                        await self.send(f'{client_data["name"]} changed their nick to {new_nick}')
                        client_data['name'] = new_nick
                else:
                    raise Exception('Not a valid command')
            except Exception:
                await self.send('Error not a valid command')

    async def send(self, msg, user=None):
        async def broadcast():
            await self.do_messages_store(msg)
            if not len(self.clients):
                print('Main-thread: No one is in the chat not broadcasting message')
            for client in self.clients:
                try:
                    client['client'].send(f"{msg}".encode('utf-8'))
                except:
                    print('Main-thread: user disconnected removing user (broken pipe)')
                    name = client['name']
                    await self.disconnect(client)
                    await self.send(name + " has left the chat")

        async def send_user():
            print(';p;')

        if not user:
            func = broadcast
        else:
            func = send_user
        if self.task in asyncio.all_tasks():
            await asyncio.wait_for(self.task, 100)
        self.task = asyncio.create_task(func())
        await self.task

    async def do_messages_store(self, msg):
        if len(self.messages) == 13:
            self.messages.remove(self.messages[0])
        self.messages.append(msg)

    async def client_thread(self, running=True):
        client_data = self.clients[self.index]
        client = client_data['client']
        username = client_data['name']
        print(f'{username}-thread: Started Thread')
        while running:
            username = client_data['name']
            try:
                msg = client.recv(1024).decode('utf-8')
                msg = msg.rstrip()
                await self.send(f'{username}:{msg}')
                await self.commands(msg, client_data)
            except:
                print(f'{username}-thread: Disconnected')
                print(f'{username}-thread: Removing from client list')
                await self.disconnect(client_data)
                running = False
        print(f'{username}-thread: Thread has stopped')


if __name__ == '__main__':
    server = Main()
    asyncio.run(server.handle())
