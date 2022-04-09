import datetime
from socket import *
from math import inf


class RTTStatistic:
    def __init__(self):
        self.rtt_min = inf
        self.rtt_max = -inf
        self.rtt_sum = 0
        self.success_cnt = 0
        self.missed_cnt = 0

    def update(self, rtt=None):
        if rtt is not None:
            self.rtt_min = min(self.rtt_min, rtt)
            self.rtt_max = max(self.rtt_max, rtt)
            self.success_cnt += 1
            self.rtt_sum += rtt
            return
        self.missed_cnt += 1

    def print(self):
        print()
        print(f'Ping statistics for 127.0.0.1:')
        print(f'Packets: Sent = {self.success_cnt + self.missed_cnt},'
              f'Received = {self.success_cnt}, '
              f'Lost = {self.missed_cnt} <{int(self.missed_cnt / (self.success_cnt + self.missed_cnt) * 100)}% loss>,')
        print(f'Approximate round trip times in milli-seconds:')
        print(f'Minimum = {int(self.rtt_min)}ms, Maximum = {int(self.rtt_max)}ms, '
              f'Average = {int(self.rtt_sum / self.success_cnt)}ms')




serverName = '127.0.0.1'
serverPort = 2000

print('Client start')
clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
clientSocket.settimeout(1)

rtt_stats = RTTStatistic()

for idx in range(10):
    cur_time = datetime.datetime.now()
    message = f'Ping {idx} {cur_time}'.encode('utf-8')
    clientSocket.sendto(message, (serverName, serverPort))

    try:
        response, _ = clientSocket.recvfrom(1024)
        response = response.decode('utf-8')
        print(response)

        request_time = cur_time
        cur_time = datetime.datetime.now()

        rtt = (cur_time - request_time).total_seconds() * 1000
        rtt_stats.update(rtt)

    except:
        print("Request timed out")
        rtt_stats.update()

rtt_stats.print()
