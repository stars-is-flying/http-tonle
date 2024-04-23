#!/usr/bin/python

import socket
import threading
import sys

args = sys.argv

if len(args) != 5:
    print("Args error!")

laddr = args[1]
lport = args[2]
rhost = args[3]
rport = args[4]

def run(client: socket.socket):
    data = client.recv(10024)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((laddr, int(lport)))
    server.send(data)
    res = server.recv(10024)
    client.send(res)
    client.close()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((rhost, int(rport)))
    server.listen(5)
    print(f"tonnle linten on port {rport}......")

    while True:
        client, addr = server.accept()
        print(f"recv data from {addr}.....")
        th = threading.Thread(target=run, args=(client,))
        th.start()

