import socket
import sys
from threading import Thread
import random
from time import sleep


class Client_thread(Thread):
    def __init__(self, client_data, parent):
        Thread.__init__(self)
        # Start thread
        # client stuff
        self.client_data = client_data
        self.client = client_data["client"]
        self.client_id = client_data["id"]
        self.username = client_data["username"]
        self.parent = parent
        # start
        print(f'{self.client_id}/Thread: Client thread has started')

    def message_loop(self, running=True):
        while running:
            try:
                message = self.client.recv(20971520).decode("utf-8")
                if not message in self.parent.error_message_sends:
                    self.parent.send_message(msg=message, from_client_data=self.client_data)

                else:
                    raise Exception
            except:
                self.disconnect()
                running = False
                break

    def disconnect(self):
        del server.clients[self.client_id]
        print(f'{self.client_id}/Thread: Client thread has stopped')

    def run(self):
        self.message_loop()


class Server:
    def __init__(self):
        print("*** Server starting ***")
        self.error_message_sends = ['']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.messages = [[]]
        if "dev" in sys.argv:
            self.sock.bind(('localhost', 8888))
        else:
            self.sock.bind(("10.1.1.4", 8888))
        print("Main/Thread: Bound Ip address and Port")
        print("Main/Thread: Server has started")

    def mainloop(self):
        self.sock.listen(1)
        print("Main/Thread: Listening for client connections")
        while True:
            client, address = self.sock.accept()
            print(f"{address[0]}: Connected to server")
            client_id = self.generate_client_id()
            print(f"{address[0]}: Has been generated a client id ({client_id})")
            try:
                client.send(str(client_id).encode('utf-8'))
                # username = client.recv(20971520).decode('utf-8')
                username = "bob"
                self.clients[client_id] = {"client": client, "id": client_id, "username": username, "ip_address": address[0]}
                self.send_all_message_lists(self.clients[client_id])
                Client_thread(self.clients[client_id], self).start()
            except:
                print(f"{address[0]}: Disconnected from server")

    def send_all_message_lists(self, client_data):
        header = {"amount_of_message_lists": len(self.messages), "server": "No"}
        self.send_message(msg=header, from_client_data=client_data, self_send=True)
        for message_list in self.messages:
            self.send_message(msg=message_list, from_client_data=client_data, self_send=True)

    def send_message(self, msg, from_client_data, to_client_data=None, self_send=False):
        sleep(0.5)
        if not to_client_data and not self_send:
            for client_id in self.clients:
                client_data = self.clients[client_id]
                message = f'{from_client_data["username"]}: {msg}'
                # add message to messages
                if len(self.messages[0]) == 20:
                    self.messages.insert(0, [])
                else:
                    self.messages[0].append(message)
                # send message to everyone
                message_data = {"user_id": client_id, "message": message}
                client_data['client'].send(str(message_data).encode('utf-8'))

        elif self_send:
            from_client_data['client'].send(str(msg).encode('utf-8'))

    def generate_client_id(self):
        client_id = random.randint(100000000000, 900000000000)
        if client_id in self.clients:
            self.generate_client_id()
        else:
            return client_id


if __name__ == '__main__':
    server = Server()
    server.mainloop()
