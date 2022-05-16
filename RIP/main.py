import argparse
import json
from math import inf


class Router:
    def __init__(self, ip, neighbors):
        self.ip = ip
        self.neighbors = neighbors
        self.dist = {}
        self.next = {}
        for neighbor in self.neighbors:
            self.dist[neighbor] = 1
            self.next[neighbor] = neighbor

    def __eq__(self, other):
        return self.ip == other.ip

    def __hash__(self):
        return hash(self.ip)

    def __str__(self):
        s = f'{"[Source IP]":20} {"[Destination IP]":20} {"[Next Hop]":20} {"Metric":5}\n'
        for router in self.dist:
            s += f'{self.ip:20} {router:20} {self.next[router]:20} {self.dist[router]:5}\n'
        return s

    def update_dist(self, router):
        is_updated = False
        for neighbor in self.neighbors:
            new_dist = router.dist.get(neighbor, inf) + 1
            if new_dist < self.dist.get(router.ip, inf):
                self.dist[router.ip] = new_dist
                self.next[router.ip] = neighbor
                is_updated = True
        return is_updated


def run_rip(network, is_simulation):
    step = 0
    while True:
        is_updated = False
        step += 1
        for start_router in network:
            for finish_router in network:
                if start_router == finish_router:
                    continue
                is_updated_now = start_router.update_dist(finish_router)
                is_updated = is_updated_now or is_updated

        if not is_updated:
            break

        if is_simulation:
            for router in network:
                print(f'Simulation step {step} of router {router.ip}')
                print(router)

    for router in network:
        print(f'Final state of router {router.ip} table:')
        print(router)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    parser.add_argument('--mode', type=str, help='Possible modes: "final", "simulation"', default='final')
    args = parser.parse_args()

    with open(args.filename, 'r') as f:
        graph = json.load(f)

    network = []
    for ip, neighbors in graph.items():
        network.append(Router(ip, neighbors))

    run_rip(network, args.mode == 'simulation')
