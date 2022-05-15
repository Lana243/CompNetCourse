from datetime import datetime
import PySimpleGUI as sg
import socket
import random


def build_message(message_len):
    message = ''
    for i in range(message_len):
        message += chr(random.randint(33, 126))
    return message


layout = [
    [sg.Text('Введите IP адрес получателя', size=(40, 1)), sg.InputText(key='host')],
    [sg.Text('Выберите порт отправки', size=(40, 1)), sg.InputText(key='port')],
    [sg.Text('Введите количество пакетов для отправки', size=(40, 1)), sg.InputText(key='num_packets')],
    [sg.Button('Отправить пакеты')],
]

window = sg.Window(title="Отправитель UDP", layout=layout, margins=(100, 50))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.settimeout(1000)

while True:
    event, values = window.read()

    if event is None:
        break

    if event != 'Отправить пакеты':
        sg.Popup(f'Unknown command', title='Error')
        continue

    try:
        host, port, num_packets = values['host'], int(values['port']), int(values['num_packets'])
    except Exception as e:
        sg.Popup(f'Invalid arguments', title='Error')
        continue

    try:
        client_socket.sendto(str(num_packets).encode('utf-8'), (host, port))

        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # client_socket.connect((host, port))
        # client_socket.sendall(bytes(str(num_packets), encoding='utf-8'))
        for i in range(num_packets):
            message = f'{int(datetime.now().timestamp() * 1000)} '
            message += build_message(1024 - len(message))
            client_socket.sendto(message.encode('utf-8'), (host, port))
    except Exception as e:
        sg.Popup(f'Sending messages failed {e}', title='Error')
        continue
