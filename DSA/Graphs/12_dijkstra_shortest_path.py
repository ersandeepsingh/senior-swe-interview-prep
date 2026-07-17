# ============================================================
# DIJKSTRA'S ALGORITHM  ->  shortest path from a source
# ------------------------------------------------------------
# Greedy + min-heap: always expand the currently-closest unsettled
# node and RELAX its edges (update a neighbour's distance if going
# through this node is cheaper). Works for non-negative weights only.
#
# NOTE: this version scans the whole `edges` list on every pop, which
# is O(V * E). Building an adjacency list first would make it the
# usual O(E log V); kept simple here to match the original.
# The edges are treated as UNDIRECTED (both endpoints relaxed).
# ============================================================
import heapq
import math


def dijkstra(V, edges, src):
    min_heap = []
    distance = [math.inf] * V             # best known distance to each node
    distance[src] = 0
    heapq.heappush(min_heap, (0, src))    # (distance, node)

    while min_heap:
        _, node = heapq.heappop(min_heap)
        for edge in edges:
            # treat edge as undirected: relax from whichever end is `node`
            if edge[0] == node:
                v, weight = edge[1], edge[2]
            elif edge[1] == node:
                v, weight = edge[0], edge[2]
            else:
                continue
            if distance[v] > distance[node] + weight:   # found a shorter path
                distance[v] = distance[node] + weight
                heapq.heappush(min_heap, (distance[v], v))
    return distance


if __name__ == '__main__':
    V = 3
    edges = [[0, 1, 1], [1, 2, 3], [0, 2, 6]]
    src = 2
    print("shortest distances from", src, ":", dijkstra(V, edges, src))
