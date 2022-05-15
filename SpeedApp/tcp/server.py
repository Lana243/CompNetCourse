import PySimpleGUI as sg
import socket
from datetime import datetime


def create_tcp_socket(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    return server_socket


layout = [[sg.Text('Введите IP', size=(40, 1)), sg.InputText(key='host')],
    [sg.Text('Выберите порт для получения', size=(40, 1)), sg.InputText(key='port')],
    [sg.Text('Скорость передачи', size=(40, 1)), sg.Text(key='speed')],
    [sg.Text('Число полученных пакетов', size=(40, 1)), sg.Text(key='num_pack_recv')],
    [sg.Button('Получить')]]

window = sg.Window(title="Получатель TCP", layout=layout, margins=(100, 50))

while True:
    event, values = window.read()

    if event is None:
        break

    if event != 'Получить':
        sg.Popup(f'Unknown command', title='Error')
        continue

    try:
        host, port = values['host'], int(values['port'])
    except Exception as _:
        sg.Popup(f'Invalid arguments', title='Error')
        continue

    host, port, num_packets = '127.0.0.1', 2000, 5
    server_socket = create_tcp_socket(host, port)

    total_packets = 0
    packets_recv = 0
    start_time = 0
    finish_time = 1

    try:
        recv_tcp_socket, _ = server_socket.accept()
        total_packets = int(recv_tcp_socket.recv(1024).decode('utf-8'))
        print(total_packets)
        for i in range(total_packets):
            try:
                packet_time_ms, _ = recv_tcp_socket.recv(1024).decode('utf-8').split()
                print(i, packet_time_ms)
                packets_recv += 1
                if start_time == 0:
                    start_time = int(packet_time_ms)
            except socket.timeout:
                pass
        finish_time = int(datetime.now().timestamp() * 1000)
        recv_tcp_socket.close()
    except Exception as e:
        sg.Popup(f'Packets receiving failed {e}', title='Error')
        recv_tcp_socket.close()
        server_socket.close()
        continue

    total_time_ms = finish_time - start_time
    speed = round(1024 * packets_recv / total_time_ms)
    window['speed'].Update(f'{speed} KB/s')
    window['num_pack_recv'].Update(f'{packets_recv} of {total_packets}')

    server_socket.close()
