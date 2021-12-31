import socket
import threading
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


ip = "127.0.0.1"
port = 8885

server_running = True

clients = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def recv_data(client: socket.socket):
    bufflen = int.from_bytes(client.recv(4), "little")
    msg = client.recv(bufflen).decode("utf-8")
    if not bufflen:
        remove_client(client)
    else:
        return msg
        # print(f"bufflen: {bufflen}")


def send_to_all(msg):
    encoded_message = len(msg).to_bytes(4, "little") + msg.encode("utf-8")

    for client in clients:
        client.send(encoded_message)


def add_client(client: socket.socket):
    clients.append(client)
    username = recv_data(client)
    print(username)


def remove_client(client: socket.socket):
    print("server: client disconnected")
    client.close()
    clients.remove(client)


def connection_listener():
    sock.listen()

    while server_running:
        conn, addr = sock.accept()
        print(f"server: connection from {addr[0]}")
        threading.Thread(target=lambda: add_client(conn), daemon=True).start()


sock.bind((ip, port))

connection_listener()
