# ============================================================
# CYCLE DETECTION in a DIRECTED graph
# ------------------------------------------------------------
# For directed graphs the "parent" trick does NOT work. Instead we
# track TWO things:
#   visited[]     -> node seen at any point
#   visitedPath[] -> node currently on the active recursion stack
# If we reach a node that is already on the current path, that's a
# back edge => cycle. On the way out we pop the node off the path.
# ============================================================
from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def dfsHelper(self, s, adjacency_list, visited, visitedPath):
        visited[s] = True
        visitedPath[s] = True             # entering: put s on current path
        for i in adjacency_list.get(s, []):
            if not visited[i]:
                if self.dfsHelper(i, adjacency_list, visited, visitedPath):
                    return True
            elif visitedPath[i]:          # neighbour already on this path -> cycle
                return True
        visitedPath[s] = False            # leaving: remove s from current path
        return False

    def DFS(self, s, adjacency_list):
        # Why do we define visited = [False] * (len(adjacency_list) + 1)?
        # In this code, 'visited' and 'visitedPath' are lists indexed by node label. The expression
        # 'len(adjacency_list)' gives the number of keys (nodes with outgoing edges), but in some
        # graphs, nodes may only appear as destinations and not as keys. Adding 1 hopes to cover all
        # possible indices from 0..n. However, if your nodes are not 0-based and continuous, or you
        # have nodes that only appear as destinations, this is not fully robust. For most simple
        # 0..n-1 graphs, this suffices, but for general graphs, you should compute the largest node
        # index and size the arrays accordingly.

        # A more robust alternative would be:
        # max_index = max([s] + list(adjacency_list.keys()) + [v for vs in adjacency_list.values() for v in vs])
        # visited = [False] * (max_index + 1)
        # visitedPath = [False] * (max_index + 1)
        # For now, keep the code as is:
        n = len(adjacency_list) + 1
        visited = [False] * n
        visitedPath = [False] * n
        cycle = self.dfsHelper(s, adjacency_list, visited, visitedPath)
        print("Cycle detected:", cycle)
    
    # BFS 
    def bfsCycleDetect(self, s, adjacency_list):
        """
        Detect cycle in a directed graph using BFS (Kahn's algorithm for topological sort).
        If there is a cycle, topological sort will NOT include all nodes (i.e., in-degree never reaches zero for all).
        Return True if a cycle exists, else False.
        """
        # Compute in-degree for each node
        from collections import deque

        # Collect all unique nodes (keys + values) to properly size in-degree map
        all_nodes = set(adjacency_list.keys())
        for vs in adjacency_list.values():
            all_nodes.update(vs)

        indegree = {node: 0 for node in all_nodes}
        for u in adjacency_list:
            for v in adjacency_list[u]:
                indegree[v] += 1

        # Collect all nodes with in-degree zero
        queue = deque([node for node in all_nodes if indegree[node] == 0])
        count = 0

        while queue:
            u = queue.popleft()
            count += 1
            for v in adjacency_list.get(u, []):  # use .get to handle possible missing keys
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)

        # If count != total nodes, there is a cycle
        has_cycle = count != len(all_nodes)
        print("Cycle detected (BFS/Kahn):", has_cycle)
        return has_cycle


if __name__ == '__main__':
    # 0 -> 1 -> 2 -> 3 -> 0  (directed cycle)
    adjacency_list = {
        0: [1, 2],
        1: [2],
        2: [3],
        3: [0],
    }

    g = Graph()
    for u in adjacency_list:
        for v in adjacency_list[u]:
            g.addEdge(u, v)

    print("Directed cycle detection starting from vertex 0:")
    g.DFS(0, adjacency_list)
