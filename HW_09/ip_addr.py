from netifaces import interfaces, ifaddresses, AF_INET


def print_ip4_addresses():
    for interface in interfaces():
        for link in ifaddresses(interface)[AF_INET]:
            print(f'addr: {link["addr"]}, netmask: {link["netmask"]}')


if __name__ == '__main__':
    print_ip4_addresses()

