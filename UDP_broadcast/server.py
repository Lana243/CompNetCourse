
import datetime
import time
from socket import *


def run_my_server():
    serverPort = 2000
    serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    serverSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    print('Start server')

    try:
        while True:
            serverSocket.sendto(datetime.datetime.now().strftime("%H:%M:%S").encode("utf-8"),
                                ("255.255.255.255", serverPort))
            time.sleep(1)
    except KeyboardInterrupt:
        serverSocket.close()
        print('Server shutdown')


run_my_server()
