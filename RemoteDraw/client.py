import socket
from utils import *


SERVER_HOST = '127.0.0.1'
SERVER_PORT = 2000


def draw(x, y):
    global window, last_point
    if last_point is None:
        window = draw_point(window, x, y)
        client_socket.sendto(f'POINT {x} {y}'.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
    else:
        window = draw_line(window, last_point[0], last_point[1], x, y)
        client_socket.sendto(f'LINE {last_point[0]} {last_point[1]} {x} {y}'.encode('utf-8'),
                             (SERVER_HOST, SERVER_PORT))


def update_client():
    global is_running_client, is_pressed_mouse, last_point, client_socket
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running_client = False
            client_socket.sendto('QUIT'.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
        elif event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and is_pressed_mouse):
            is_pressed_mouse = True
            x, y = pygame.mouse.get_pos()
            draw(x, y)
            last_point = (x, y)
        elif event.type == pygame.MOUSEBUTTONUP:
            is_pressed_mouse = False
            last_point = None


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

window = pygame_start('Client')
is_running_client = True
is_pressed_mouse = False
last_point = None

while is_running_client:
    update_client()
    pygame.display.update()

pygame.quit()
client_socket.close()
