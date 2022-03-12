from socket import *
from threading import Thread
from time import sleep


def client_process(client_socket, client_addr):
    print(f'Start processing new client on {client_addr[0]}:{client_addr[1]}')
    request = client_socket.recv(1024).decode('utf-8')
    content = load_page(request)
    # uncomment sleep to check multithreading
    # sleep(10)
    client_socket.send(content)
    print('Response sent')
    client_socket.shutdown(SHUT_WR)


def run_my_server():
    serverPort = 2000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('127.0.0.1', serverPort))
    serverSocket.listen(1)
    print('Start server')

    try:
        while True:
            print("Wait for new connection...")
            connectionSocket, addr = serverSocket.accept()
            Thread(target=client_process, args=(connectionSocket, addr)).start()
    except KeyboardInterrupt:
        serverSocket.close()
        print('Server shutdown')


def load_page(request):
    HDRS = 'HTTP/1.1 200 OK\r\nContent-type: text/html; charset=utf-8\r\n\r\n'.encode('utf-8')
    HDRS404 = 'HTTP/1.1 404 Not found\r\nContent-type: text/html; charset=utf-8\r\n\r\n'.encode('utf-8')
    path = 'dir/' + request.split()[1]
    try:
        with open(path, 'rb') as file:
            resp = file.read()
    except FileNotFoundError:
        return HDRS404 + 'File not found'.encode('utf-8')
    return HDRS + resp


run_my_server()
