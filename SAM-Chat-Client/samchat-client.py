import socket
import threading

ip = "127.0.0.1"
port = 8812

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((ip, port))
except socket.error:
    print("Falied to connect to the socket")


def send_message(msg: str):
    encoded_message = len(msg).to_bytes(4, "little") + msg.encode("utf-8")
    sock.send(encoded_message)


def receive_message():
    while True:
        bufflen = int.from_bytes(sock.recv(4), "little")
        msg = sock.recv(bufflen).decode("utf-8")
        if bufflen:
            print(f"\n{msg}")


send_message(input("What do you want your username to be? "))

threading.Thread(target=receive_message, daemon=True).start()
running = True
while running:
    data = input("\nMessage: ")
    if not data == "!exit":
        send_message(data)
    else:
        running = False


sock.close()
