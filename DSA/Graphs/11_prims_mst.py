# ============================================================
# PRIM'S ALGORITHM  ->  Minimum Spanning Tree (MST) cost
# ------------------------------------------------------------
# Grow the MST one vertex at a time. A min-heap always hands us the
# cheapest edge leaving the tree. Add that vertex, then push its new
# outgoing edges. Skip vertices already in the tree.
# Time ~ O(E log V).
# ============================================================
from heapq import heappush, heappop


def prims_algorithm(V, edges):
    min_cost = 0
    min_heap = []
    mst_set = [False] * V                 # is vertex already in the MST?

    # adjacency list: adj[u] = list of (neighbour, weight)
    adj = [[] for _ in range(V)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    heappush(min_heap, (0, 0))            # (weight, start vertex)

    while min_heap:
        weight, u = heappop(min_heap)     # cheapest edge to a new vertex
        if not mst_set[u]:
            mst_set[u] = True
            min_cost += weight
            for v, w in adj[u]:
                if not mst_set[v]:
                    heappush(min_heap, (w, v))

    if not all(mst_set):
        return None                       # graph is disconnected -> no MST
    return min_cost


def main():
    V = 5                                 # number of vertices (cities)
    edges = [                             # [from, to, weight]
        [0, 1, 2],
        [0, 3, 6],
        [1, 2, 3],
        [1, 3, 8],
        [1, 4, 5],
        [2, 4, 7],
        [3, 4, 9],
    ]
    print("MST cost:", prims_algorithm(V, edges))


if __name__ == "__main__":
    main()
