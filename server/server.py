import socket
import asyncio
from time import sleep
from threading import Thread
from datetime import datetime


class Main:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.task = None
        self.clients = []

    async def handle(self):
        try:
            self.sock.bind(('192.168.0.69', 2288))
        except:
            self.sock.bind(('localhost', 2288))
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
        if self.task in asyncio.all_tasks():
            await asyncio.wait_for(self.task, 100)
        self.task = asyncio.create_task(self.broadcast(username + " has joined the chat"))
        await self.task
        # start new client thread
        Thread(target=lambda:asyncio.run(self.client_thread())).start()

    async def disconnect(self, client):
        name = client["name"]
        self.clients.remove(client)
        if self.task in asyncio.all_tasks():
            await asyncio.wait_for(self.task, 100)
        self.task = asyncio.create_task(self.broadcast(name + " has left the chat"))
        await self.task

    async def broadcast(self, msg):
        if not len(self.clients):
            print('Main-thread: No one is in the chat not broadcasting message')
        for client in self.clients:
            try:
                client['client'].send(f"{msg}".encode('utf-8'))
            except:
                print('Main-thread: user disconnected removing user (broken pipe)')
                name = client['name']
                await self.disconnect(client)
                await self.do_broad_task(name + " has left the chat")

    async def commands(self, msg, client_data):
        msg = str(msg)
        if msg.startswith('.'):
            print('checking messages for commands')
            if 'change_nick:' in msg:
                new_nick = msg.replace('.change_nick:', '')
                await self.do_broad_task(f'{client_data["name"]} changed their nick to {new_nick}')
                client_data['name'] = new_nick.rstrip()

    async def do_broad_task(self, msg=None):
        if self.task in asyncio.all_tasks():
            await asyncio.wait_for(self.task, 100)
        self.task = asyncio.create_task(self.broadcast(msg))
        await self.task

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
                await self.do_broad_task(f'{username}:{msg}')
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
