import socket
import uuid
from getmac import get_mac_address

from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp

import PySimpleGUI as sg


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    home_ip = s.getsockname()[0]
    s.close()
    network_ip = home_ip.split('.')
    network_ip[-1] = '0'
    network_ip = '.'.join(network_ip)
    return home_ip, network_ip


def get_hostname(ip):
    try:
        ans = socket.gethostbyaddr(ip)[0]
    except Exception as e:
        return 'Unknown host'
    return ans


def scan(ip):
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
    ans, _ = srp(request, timeout=1, retry=1)
    result = []
    for sent, received in ans:
        result.append({'IP': received.psrc, 'MAC': received.hwsrc})
    return result


home_ip, network_ip = get_my_ip()
home_mac = get_mac_address(ip=home_ip)
clients = scan(f'{network_ip}/24')

# This is the normal print that comes with simple GUI
sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)

# this is clobbering the print command, and replacing it with sg's Print()
print = sg.Print

layout = [
    [sg.ProgressBar(len(clients), orientation='h', size=(54, 20), key='progress_bar')],
    [sg.Output(size=(100, 30))],
    [sg.Submit('Start')]
]
window = sg.Window('LocalNetScanner', layout)

while True:
    event, values = window.read(timeout=1000)

    if event is None or event == 'Exit':
        break

    if event == 'Start':
        print(f'{"IP address":30}{"MAC address":30}{"Hostname":30}')
        print('Home:')
        print(f'{home_ip:30}{home_mac:30}{get_hostname(home_ip):30}')

        progress_bar = window['progress_bar']
        for i, host in enumerate(clients):
            ip, mac = host['ip'], host['mac']
            if ip == home_ip:
                continue
            print(f'{str(ip):30}{str(mac):30}{str(get_hostname(ip)):30}')
            progress_bar.UpdateBar(i + 1)

window.close()
