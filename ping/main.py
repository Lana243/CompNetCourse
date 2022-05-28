
import argparse
import socket
import os
from enum import Enum
from time import time, sleep
import struct
from select import select
import numpy as np


ICMP_ECHO_REPLY = 0
ICMP_DESTINATION_UNREACHABLE = 3
ICMP_ECHO_REQUEST = 8


class PingError(Enum):
    OPERATION_TIMEOUT = -1
    NET_UNREACHABLE = 0
    HOST_UNREACHABLE = 1
    PROTOCOL_UNREACHABLE = 2
    PORT_UNREACHABLE = 3
    FRAGMENTATION_NEEDED_AND_DO_NOT_FRAGMENT_WAS_SENT = 4
    SOURCE_ROUTE_FAILED = 5
    DESTINATION_NETWORK_UNKNOWN = 6
    DESTINATION_HOST_UNKNOWN = 7
    SOURCE_HOST_ISOLATED = 8
    COMMUNICATION_WITH_DESTINATION_NETWORK_IS_ADMINISTRATIVELY_PROHIBITED = 9
    COMMUNICATION_WITH_DESTINATION_HOST_IS_ADMINISTRATIVELY_PROHIBITED = 10
    DESTINATION_NETWORK_UNREACHABLE_FOR_TYPE_OF_SERVICE = 11
    DESTINATION_HOST_UNREACHABLE_FOR_TYPE_OF_SERVICE = 12
    COMMUNICATION_ADMINISTRATIVELY_PROHIBITED = 13
    HOST_PRECEDENCE_VIOLATION = 14
    PRECEDENCE_CUTOFF_IN_EFFECT = 15


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('--timeout', default=5, type=int)
    args = parser.parse_args()
    return args.host, args.timeout


def parse_icmp_packet(packet):
    icmp_part = packet[20:]
    type, code = struct.unpack('bb', icmp_part[:2])
    if type == ICMP_ECHO_REPLY and code == 0:
        header = icmp_part[:8]
        data = icmp_part[8:]
        type, code, checksum, p_id, p_seq = struct.unpack("bbHHh", header)
        return type, code, (checksum, p_id, p_seq, data)
    elif type == ICMP_DESTINATION_UNREACHABLE:
        return type, code, icmp_part[34:34 + 64]
    else:
        return type, code, icmp_part[2:]


def get_checksum(packet, reverse=True):
    ans = 0
    for i in range(0, len(packet), 2):
        ans += packet[i]
        if i + 1 < len(packet):
            ans += (packet[i + 1] << 8)
    while (ans & 0xFFFF) != ans:
        ans = (ans >> 16) + (ans & 0xFFFF)
    if reverse:
        ans ^= 0xFFFF
    return ans


def construct_request(packet_id, seq):
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, packet_id, seq)
    data = struct.pack("d", time())
    checksum = get_checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, checksum, packet_id, seq)
    return header + data


def ping_send(client_socket, host, packet_id, seq):
    echo_packet = construct_request(packet_id, seq)
    client_socket.sendto(echo_packet, (host, 1))


def is_correct_packet(type, code, id, seq, data, checksum):
    return get_checksum(struct.pack("bbHHh", type, code, 0, id, seq) + data, False) + checksum == 0xffff


def ping_recv(client_socket, packet_id, seq, timeout):
    start_time = time()

    while timeout > 0:
         select_time = time()
         ready = select([client_socket], [], [], timeout)
         select_time = time() - select_time

         if not ready[0]:
             return time() - start_time, PingError.OPERATION_TIMEOUT

         recv_time = time()
         recv, _ = client_socket.recvfrom(1024)
         p_type, p_code, p_other = parse_icmp_packet(recv)

         if p_type == ICMP_ECHO_REPLY and p_code == 0:
             p_checksum, p_id, p_seq, p_data = p_other
             if p_id == packet_id and p_seq == seq and is_correct_packet(p_type, p_code, p_id, p_seq, p_data, p_checksum):
                 return recv_time - start_time, None
         elif p_type == ICMP_DESTINATION_UNREACHABLE:
             _, _, (_, p_id, p_seq, _) = parse_icmp_packet(p_other)
             if p_id == packet_id and p_seq == seq:
                 return recv_time - start_time, PingError(p_code)
         timeout -= select_time

    return time() - start_time, PingError.OPERATION_TIMEOUT


def ping(host, seq, timeout):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    packet_id = os.getpid() & 0xFFFF
    ping_send(client_socket, host, packet_id, seq)
    delay, err = ping_recv(client_socket, packet_id, seq, timeout)
    client_socket.close()
    return delay, err


if __name__ == '__main__':
    host, timeout = parse_arguments()
    seq = 0
    start_time = time()
    rtt = []
    try:
        dest = socket.gethostbyname(host)
        print(f'PING {host} ({dest})')
        while True:
            seq += 1
            delay, err = ping(dest, seq, timeout)
            if err is None:
                rtt.append(delay * 1000)
                print(f'Received ICMP echo reply from {dest}: icmp_seq={seq} time={delay * 1000 :.3f} ms')
            else:
                print(f'Error occurred: {err.name}')
            sleep(1)
    except KeyboardInterrupt:
        print()
        total_time = (time() - start_time) * 1000
        print(f'{seq} packets transmitted, {len(rtt)} packets received, {round((1 - len(rtt) / seq) * 100)}% packet loss, time {round(total_time)}ms')
        if len(rtt) > 0:
            rtt = np.array(rtt)
            print(f'rtt min/avg/max/mdev = {min(rtt):.3f}/{rtt.mean():.3f}/{max(rtt):.3f}/{rtt.std():.3f} ms')
