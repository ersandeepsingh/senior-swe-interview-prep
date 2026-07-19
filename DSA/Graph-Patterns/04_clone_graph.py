# Clone Graph
#
# LeetCode: 133
# Difficulty: Medium
# Pattern: Clone graph
#
# Problem:
# Given a reference of a node in a connected undirected graph, return a deep copy (clone)
# of the graph.
#
# Each node in the graph contains a value (int) and a list (List[Node]) of its neighbors.
#
# Example 1:
# Input: adjList = [[2, 4], [1, 3], [2, 4], [1, 3]]
# Output: [[2, 4], [1, 3], [2, 4], [1, 3]]
#
# Example 2:
# Input: adjList = [[]]
# Output: [[]]
#
# Example 3:
# Input: adjList = []
# Output: []
#
# Constraints:
# - The number of nodes in the graph is in the range [0, 100]
# - 1 <= Node.val <= 100
# - Node.val is unique for each node
# - There are no repeated edges and no self-loops in the graph
# - The Graph is connected and all nodes can be visited starting from the given node

class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def clone_graph(node):
    pass


if __name__ == '__main__':
    n1, n2, n3, n4 = Node(1), Node(2), Node(3), Node(4)
    n1.neighbors = [n2, n4]
    n2.neighbors = [n1, n3]
    n3.neighbors = [n2, n4]
    n4.neighbors = [n1, n3]
    ans = clone_graph(n1)
    print(ans)
