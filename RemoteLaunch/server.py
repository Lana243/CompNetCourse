from socket import *
import subprocess


def client_process(client_socket, client_addr):
    print(f'Start processing new client on {client_addr[0]}:{client_addr[1]}')
    request = client_socket.recv(1024).decode('utf-8')
    return_code = subprocess.call(request, shell=True)
    client_socket.send(f'Returned code {return_code}'.encode("utf-8"))
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
            client_process(connectionSocket, addr)
    except KeyboardInterrupt:
        serverSocket.close()
        print('Server shutdown')


run_my_server()
