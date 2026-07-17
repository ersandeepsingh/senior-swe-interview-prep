# ============================================================
# GRAPH DFS  (adjacency-list representation)
# ------------------------------------------------------------
# DFS dives as deep as possible before backtracking, using the
# recursion call stack. Mark visited as you enter each node.
# ============================================================
# NOTE: removed junk "from asyncio import queues" import (unused).
from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def dfsHelper(self, s, visited):
        for i in self.graph[s]:
            if not visited[i]:
                print(i, " ")
                visited[i] = True
                self.dfsHelper(i, visited)   # recurse deeper first

    def DFS(self, s):
        # Calculate max_node: We find the highest-numbered node in the graph (the maximum node id).
        # This is done by looking at both:
        # - all source nodes (the keys of self.graph), and
        # - all destination nodes (every neighbor listed in the adjacency lists, i.e., all values in self.graph.values()).
        # The first max(self.graph) gets the largest key (source node).
        # The second max(...) with the generator gets the largest destination node appearing in any list of neighbors.
        # Taking max() of both ensures we don't miss nodes that only appear as destinations.
        max_node = max(max(self.graph), max(v for vs in self.graph.values() for v in vs))
        visited = [False] * (max_node + 1)
        visited[s] = True
        print(s, " ")
        self.dfsHelper(s, visited)


if __name__ == '__main__':
    g = Graph()
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(1, 2)
    g.addEdge(2, 0)
    g.addEdge(2, 3)
    g.addEdge(3, 4)

    print("DFS starting from vertex 2:")
    g.DFS(2)
