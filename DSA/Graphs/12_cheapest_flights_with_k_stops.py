# Cheapest Flights Within K Stops

# There are n cities connected by some number of flights. You are given an array flights
# where flights[i] = [fromi, toi, pricei] indicates that there is a flight from city fromi to
# city toi with cost pricei.

# You are also given three integers src, dst, and k, return the cheapest price from
# src to dst with at most k stops. If there is no such route, return -1.

import math
from typing import List
from collections import deque


def findCheapestPrice(n: int, flights: List[List[int]], src: int, dst: int, k: int):
    adjList = [[] for _ in range(n)]
    for u, v, wt in flights:
        adjList[u].append([v, wt])

    INF = math.inf
    min_cost = [INF] * n
    # FIX 1: start from src (old code used leftover `u` from the flights loop)
    min_cost[src] = 0

    # [city, cost_so_far] — same idea as before, but expand one hop (one flight) per level
    queue = deque()
    queue.append([src, 0])

    # FIX 2: at most k stops => at most (k + 1) flights => (k + 1) BFS levels.
    # Old code used list.pop() (DFS) + jumps check; that broke stop counting / pruning.
    flights_left = k + 1
    while queue and flights_left > 0:
        # Only process nodes already in the queue for THIS hop (snapshot size).
        size = len(queue)
        for _ in range(size):
            # FIX 3: popleft = BFS (old list.pop() was LIFO / DFS)
            u, cost = queue.popleft()

            for v, wt in adjList[u]:
                # FIX 4: new cost is path cost + edge weight.
                # Old code used `cost + min_cost[u]`, which ignored `wt`.
                new_cost = cost + wt
                if new_cost < min_cost[v]:
                    min_cost[v] = new_cost
                    queue.append([v, new_cost])
        flights_left -= 1

    return -1 if min_cost[dst] == INF else min_cost[dst]


if __name__ == "__main__":
    # Example usage
    n = 4
    flights = [
        [0, 1, 100],
        [1, 2, 100],
        [2, 3, 100],
        [0, 2, 500],
    ]
    src = 0
    dst = 3
    k = 1

    price = findCheapestPrice(n, flights, src, dst, k)
    print(
        "Cheapest price from {} to {} with at most {} stops: {}".format(
            src, dst, k, price
        )
    )
