from utils import *
import socket
import pygame


SERVER_HOST = '127.0.0.1'
SERVER_PORT = 2000


def update_server():
    global server_socket, window, is_running_server
    request = server_socket.recvfrom(1024)[0].decode('utf-8').split()
    if request[0] == 'QUIT':
        is_running_server = False
    elif request[0] == 'POINT':
        window = draw_point(window, int(request[1]), int(request[2]))
    elif request[0] == 'LINE':
        window = draw_line(window, int(request[1]), int(request[2]), int(request[3]), int(request[4]))


window = pygame_start('Server')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))

is_running_server = True

while is_running_server:
    update_server()
    pygame.display.update()

pygame.quit()
server_socket.close()
