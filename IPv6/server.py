from socket import *

server_host = "::1"
server_port = 2000

server_socket = socket(AF_INET6, SOCK_DGRAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.bind((server_host, server_port))

try:
    print('Server started')
    while True:
        request, addr = server_socket.recvfrom(1024)
        response = request.decode('utf-8').upper().encode('utf-8')
        server_socket.sendto(response, addr)
except KeyboardInterrupt:
    print('Server shut down')

