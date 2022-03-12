import sys
from socket import *

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
fileName = sys.argv[3]

print('Client start')
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
request = ('GET /' + fileName + ' HTTP/1.1').encode('utf-8')
clientSocket.send(request)

resp = clientSocket.recv(1024).decode('utf-8')
print('Server response:')
print(resp)
print('Client close')
clientSocket.close()
