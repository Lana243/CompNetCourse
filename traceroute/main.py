import argparse
import socket
import os
from time import time
import struct
from select import select


ICMP_ECHO_REPLY = 0
ICMP_DESTINATION_UNREACHABLE = 3
ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('-N', default=3, type=int)
    parser.add_argument('--timeout', default=5, type=int)
    args = parser.parse_args()
    return args.host, args.N, args.timeout


def parse_icmp_packet(packet):
    icmp_part = packet[20:]
    type, code = struct.unpack('bb', icmp_part[:2])
    if type == ICMP_ECHO_REPLY and code == 0:
        header = icmp_part[:8]
        data = icmp_part[8:]
        type, code, checksum, p_id, p_seq = struct.unpack("bbHHh", header)
        return type, code, (checksum, p_id, p_seq, data)
    elif type in {ICMP_TIME_EXCEEDED, ICMP_DESTINATION_UNREACHABLE}:
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


def traceroute_send(client_socket, host, packet_id, seq):
    echo_packet = construct_request(packet_id, seq)
    client_socket.sendto(echo_packet, (host, 1))


def is_correct_packet(type, code, id, seq, data, checksum):
    return get_checksum(struct.pack("bbHHh", type, code, 0, id, seq) + data, False) + checksum == 0xffff


def traceroute_recv(client_socket, packet_id, seq, timeout):
    start_time = time()
    addr = None

    while timeout > 0:
         select_time = time()
         ready = select([client_socket], [], [], timeout)
         select_time = time() - select_time

         if not ready[0]:
             return time() - start_time, ICMP_DESTINATION_UNREACHABLE, -1, addr

         recv_time = time()
         recv, addr = client_socket.recvfrom(1024)
         p_type, p_code, p_other = parse_icmp_packet(recv)

         if p_type == ICMP_ECHO_REPLY and p_code == 0:
             p_checksum, p_id, p_seq, p_data = p_other
             if p_id == packet_id and p_seq == seq and is_correct_packet(p_type, p_code, p_id, p_seq, p_data, p_checksum):
                 return recv_time - start_time, p_type, p_code, addr
         elif p_type == ICMP_TIME_EXCEEDED and p_code == 0:
             return recv_time - start_time, p_type, p_code, addr
         elif p_type == ICMP_DESTINATION_UNREACHABLE:
             _, _, (_, p_id, p_seq, _) = parse_icmp_packet(p_other)
             if p_id == packet_id and p_seq == seq:
                 return recv_time - start_time, p_type, p_code, addr
         timeout -= select_time

    return time() - start_time, ICMP_DESTINATION_UNREACHABLE, -1, addr


def traceroute(host, seq, ttl, timeout):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    packet_id = os.getpid() & 0xFFFF
    traceroute_send(client_socket, host, packet_id, seq)
    delay, resp_type, resp_code, addr = traceroute_recv(client_socket, packet_id, seq, timeout)
    client_socket.close()
    return delay, resp_type, resp_code, addr


if __name__ == '__main__':
    host, n_requests, timeout = parse_arguments()

    seq = 0
    host_addr = socket.gethostbyname(host)
    ttl = 0

    print(f'Tracing route to {host} [{host_addr}]')
    while True:
        ttl += 1
        delays = []
        addr = None
        is_success = False
        for _ in range(n_requests):
            seq += 1
            rtt, resp_type, resp_code, cur_addr = traceroute(host_addr, seq, ttl, timeout)
            rtt *= 1000

            if addr is None:
                addr = cur_addr
            if resp_type == ICMP_DESTINATION_UNREACHABLE:
                delays.append('*')
            elif resp_type in [ICMP_ECHO_REPLY, ICMP_TIME_EXCEEDED]:
                delays.append(f'{round(rtt, 3)} ms')
                if resp_type == ICMP_ECHO_REPLY:
                    is_success = True
            if addr is None:
                print(f'{ttl}  ' + ' '.join(delays))
                continue
            try:
                hostname = socket.gethostbyaddr(cur_addr[0])[0]
            except socket.herror:
                hostname = cur_addr[0]
            print(f'{ttl}  {hostname} ({cur_addr[0]})  ', end='')
            if set(delays) == set('*'):
                print(' '.join(delays))
            else:
                print('  '.join(delays))
            if is_success:
                break
