# ============================================================
# TREE TRAVERSALS  (start here)
# ------------------------------------------------------------
# BFS  -> level order, uses a queue
# DFS  -> pre-order, uses recursion (call stack)
# BFS_by_level -> level order but grouped as [[lvl0], [lvl1], ...]
# ============================================================
from collections import deque


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def BFS(root):
    """Level-order traversal as a single flat list. Time O(n), Space O(n)."""
    if root is None:
        return []

    order = []
    queue = deque([root])
    while queue:
        node = queue.popleft()          # take from the front (FIFO)
        order.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return order


def DFS(root):
    """Depth-first pre-order (root -> left -> right). Time O(n)."""
    if root is None:
        return []

    order = []

    def dfs_helper(node):
        if node is None:
            return
        order.append(node.val)          # visit root first (pre-order)
        dfs_helper(node.left)
        dfs_helper(node.right)

    dfs_helper(root)
    return order


def BFS_by_level(root):
    """Level order grouped per level: [[level0], [level1], ...].
    Key trick: capture len(queue) BEFORE the inner loop so we only
    process the nodes belonging to the current level."""
    if root is None:
        return []

    levels = []
    queue = deque([root])
    while queue:
        level_size = len(queue)         # number of nodes on this level
        current_level = []
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(current_level)
    return levels


def main():
    #         1
    #        / \
    #       2   3
    #      / \   \
    #     4   5   6
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    root.right.right = Node(6)

    print("BFS (flat):     ", BFS(root))
    print("DFS (pre-order):", DFS(root))
    print("BFS (by level): ", BFS_by_level(root))


if __name__ == "__main__":
    main()
