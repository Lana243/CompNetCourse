from socket import *
import sys

server_host = "::1"
server_port = 2000
request = sys.argv[1]

client_socket = socket(AF_INET6, SOCK_DGRAM)
client_socket.connect((server_host, server_port))

print(f'Client request: {request}')
client_socket.send(request.encode('utf-8'))
response = client_socket.recv(1024).decode('utf-8')
print(f'Server response: {response}')
