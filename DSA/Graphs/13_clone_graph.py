"""
# Definition for a Node.
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
"""

from typing import Optional
from collections import deque

# Definition for a Node.
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

class Solution:
    def cloneGraph(self, node: 'Node') -> 'Node':
        if not node: return node
        
        q, clones = deque([node]), {node.val: Node(node.val, [])}
        while q:
            cur = q.popleft() 
            cur_clone = clones[cur.val]            

            for ngbr in cur.neighbors:
                if ngbr.val not in clones:
                    clones[ngbr.val] = Node(ngbr.val, [])
                    q.append(ngbr)
                cur_clone.neighbors.append(clones[ngbr.val])
        return clones[node.val]

    # DFS version of cloneGraph
    def cloneGraphDFS(self, node: 'Node') -> 'Node':
        if not node:
            return node
        clones = {}

        def dfs(curr):
            if curr.val in clones:
                return clones[curr.val]
            # Clone the current node (but neighbors will be added as we recurse)
            clone = Node(curr.val, [])
            clones[curr.val] = clone
            for neighbor in curr.neighbors:
                clone.neighbors.append(dfs(neighbor))
            return clone

        return dfs(node)

def print_graph(node: 'Node'):
    # Helper function to print the graph in adjacency list form (BFS order)
    if not node:
        print("Empty graph")
        return
    visited = set()
    q = deque([node])
    while q:
        curr = q.popleft()
        if curr.val in visited:
            continue
        visited.add(curr.val)
        neighbor_vals = [n.val for n in curr.neighbors]
        print(f'Node {curr.val}: Neighbors -> {neighbor_vals}')
        for n in curr.neighbors:
            if n.val not in visited:
                q.append(n)

if __name__ == "__main__":
    # Build a simple undirected graph:
    # 1 -- 2
    # |    |
    # 4 -- 3
    node1 = Node(1)
    node2 = Node(2)
    node3 = Node(3)
    node4 = Node(4)
    node1.neighbors = [node2, node4]
    node2.neighbors = [node1, node3]
    node3.neighbors = [node2, node4]
    node4.neighbors = [node1, node3]

    print("Original graph:")
    print_graph(node1)

    solution = Solution()
    clone = solution.cloneGraph(node1)
    print("\nCloned graph:")
    print_graph(clone)

    # Also test DFS version
    clone_dfs = solution.cloneGraphDFS(node1)
    print("\nCloned graph using DFS:")
    print_graph(clone_dfs)