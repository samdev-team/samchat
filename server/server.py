import socket
import asyncio
from threading import Thread
from datetime import datetime
import re


class Main:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sys = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.task = None
        self.clients = []
        self.messages = []
        self.cmd_names = [['change_nick', 'nick']]
        try:
            self.sock.bind(('192.168.0.69', 2288))
            self.sys.bind(('192.168.0.69', 2289))
        except:
            self.sock.bind(('localhost', 2288))
            self.sys.bind(('localhost', 2289))

    async def handle(self):
        self.sock.listen(1)
        self.sys.listen(1)
        print('Main-thread: Listening for connections')
        while True:
            s, a = self.sock.accept()
            s1, a1 = self.sys.accept()
            print(f'Main-thread: {a[0]} has connected')
            try:
                username = s.recv(4096).decode('utf-8').replace(' ', '_')
                await self.connect(s, s1, username)
            except Exception as e:
                print('Error:', e)
                print(f'Main-thread: {a[0]} has disconnected')

    async def connect(self, s, s1, username):
        self.clients.append({'name':username, 'client':s, "client1": s1})
        self.index = len(self.clients) - 1
        await self.send(self.messages, s1)
        await asyncio.sleep(0.1)
        users = []
        for i in self.clients:
            users.append(i['name'])
        await self.send(users, s1)
        Thread(target=lambda:asyncio.run(self.client_thread()), daemon=True).start()
        await self.send(username + " has joined the chat")

    async def disconnect(self, client):
        self.clients.remove(client)
        await self.send(client['name'] + " has left the chat")

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
                        client_data['client1'].send(f'sys_htas2789 user_changed_nick {client_data["name"]} {new_nick}'.encode('utf-8'))
                        client_data['name'] = new_nick
                else:
                    raise Exception('Not a valid command')
            except Exception as e:
                await self.send(f'Error: {e}')

    async def send(self, msg, client=None, destination=None):
        async def broadcast():
            if not msg.startswith('sys_htas2789'):
                self.messages.append(msg)
            if not len(self.clients):
                print('Main-thread: No one is in the chat not broadcasting message')
            for client_data in self.clients:
                try:
                    await send_msg(client_data['client'])
                except Exception as e:
                    print('Error: ', e)
                    print('Main-thread: user disconnected removing user')
                    await self.disconnect(client)
                    await self.send(client['name'], " has left the chat")

        async def send_msg(socket_client):
            socket_client.send(str(msg).encode('utf-8'))
            await asyncio.sleep(0.1)

        if client:
            await send_msg(client)
        elif client and destination:
            func = None
        else:
            await broadcast()

    async def client_thread(self, running=True):
        client_data = self.clients[self.index]
        client = client_data['client']
        username = client_data['name']
        print(f'{username}-thread: Started Thread')
        while running:
            username = client_data['name']
            try:
                msg = client.recv(4096).decode('utf-8')
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
