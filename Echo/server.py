import time
from socket import *
import random


def process_request(server_socket, request, client_addr):
    if random.randint(0, 5) == 0:
        return
    time.sleep(random.random())
    response = request.decode('utf-8').upper().encode('utf-8')
    server_socket.sendto(response, client_addr)


def run_my_server():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(('127.0.0.1', 2000))

    try:
        while True:
            request, addr = serverSocket.recvfrom(1024)
            process_request(serverSocket, request, addr)
    except KeyboardInterrupt:
        serverSocket.close()
        print('Server shutdown')


random.seed(243)
run_my_server()


