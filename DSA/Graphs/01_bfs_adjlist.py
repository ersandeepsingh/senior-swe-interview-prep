# ============================================================
# GRAPH BFS  (adjacency-list representation)  -- start here
# ------------------------------------------------------------
# BFS explores level by level using a queue. Mark a node visited
# the moment you ENQUEUE it, so it never gets added twice.
# ============================================================
# NOTE: removed junk "from asyncio import queues" import (unused).
from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)   # node -> list of neighbours

    def addEdge(self, u, v):
        self.graph[u].append(v)          # directed edge u -> v

    def BFS(self, s):
        visited = [False] * (max(self.graph) + 1)

        queue = []
        queue.append(s)
        visited[s] = True                # mark on enqueue (not on dequeue)

        while queue:
            u = queue.pop(0)             # dequeue from front
            print(u, end=" ")
            for i in self.graph[u]:
                if not visited[i]:
                    queue.append(i)
                    visited[i] = True


if __name__ == '__main__':
    g = Graph()
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(1, 2)
    g.addEdge(2, 0)
    g.addEdge(2, 3)
    g.addEdge(3, 3)

    print("BFS starting from vertex 0:")
    g.BFS(0)
    print()
