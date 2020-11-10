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
        self.cmd_names = [['change_nick', 'nick']]
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
                username = s.recv(1024).decode('utf-8').replace(' ', '_')
                await self.connect(s, username)
            except Exception as e:
                print('Error: ', e)
                print(f'Main-thread: {a[0]} has disconnected')

    async def connect(self, s, username):
        self.clients.append({'name':username, 'client':s})
        self.index = len(self.clients) - 1
        s.send(str(self.messages).encode('utf-8'))
        await self.wait_for_check(s)
        users = []
        for i in self.clients:
            users.append(i['name'])
        s.send(str(users).encode('utf-8'))
        await self.wait_for_check(s)
        Thread(target=lambda:asyncio.run(self.client_thread()), daemon=True).start()
        await self.send(username + " has joined the chat")


    async def wait_for_check(self, s):
        async def recv():
            s.recv(1024)
        task = asyncio.create_task(recv())
        await task
        await asyncio.wait_for(task, 100)

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
                if cmd in self.cmd_names[0]:
                    new_nick = ' '.join(all_args).replace(' ', '_')
                    if new_nick.startswith(' '):
                        raise Exception(f'Cannot change nick to "{new_nick}"')
                    elif new_nick == client_data['name']:
                        raise Exception(f'Cannot change nick to "{new_nick}"')
                    else:
                        await self.send(f'{client_data["name"]} changed their nick to {new_nick}')
                        await self.send(f'sys_htas2789 user_changed_nick {client_data["name"]} {new_nick}')
                        client_data['name'] = new_nick
                else:
                    raise Exception('Not a valid command')
            except Exception as e:
                await self.send(f'Error: {e}')

    async def send(self, msg, user=None):
        async def broadcast():
            if not msg.startswith('sys_htas2789'):
                await self.do_messages_store(msg)
            if not len(self.clients):
                print('Main-thread: No one is in the chat not broadcasting message')
            for client in self.clients:
                try:
                    client['client'].send(f"{msg}".encode('utf-8'))
                    await self.wait_for_check(client['client'])
                except Exception as e:
                    print('Error: ', e)
                    print('Main-thread: user disconnected removing user')
                    await self.disconnect(client)
                    await self.send(client['name'], " has left the chat")

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
