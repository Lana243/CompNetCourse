import socket
import sys


def get_free_ports(host_ip, ports_range):
    free_ports = []
    for port in ports_range:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex((host_ip, port)) != 0:
            free_ports.append(port)
    return free_ports


if __name__ == '__main__':
    print(*get_free_ports(sys.argv[1], range(int(sys.argv[2]), int(sys.argv[3]))))
