
import sys
from socket import *


print('Client start')
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
clientSocket.bind(("", 2000))

try:
    while True:
        response = clientSocket.recvfrom(1024)
        time = "Current time: {}".format(response[0].decode("utf-8"))
        print(time)
except KeyboardInterrupt:
    print('Client close')
    clientSocket.close()
