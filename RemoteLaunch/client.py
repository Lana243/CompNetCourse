import sys
from socket import *

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
shell_command = sys.argv[3]

print('Client start')
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
clientSocket.send(shell_command.encode("utf-8"))

resp = clientSocket.recv(1024).decode('utf-8')
print('Server response:')
print(resp)
print('Client close')
clientSocket.close()
