# ============================================================
# BASIC RECURSIVE TREE METRICS
# ------------------------------------------------------------
# countNode  -> total number of nodes
# heightDFS  -> height (number of nodes on longest root->leaf path)
# heightBFS  -> same height, computed level by level
# sumNode    -> sum of all node values
# diameter   -> longest path between any two nodes
#
# Pattern: almost every metric = solve(left) + solve(right) + self
# ============================================================
# NOTE: removed junk "from turtle import right" import (unused, and
#       importing turtle can pop up a graphics window on some systems).
from collections import deque


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def countNode(root):
    """Total nodes = 1 (self) + nodes on left + nodes on right."""
    if root is None:
        return 0
    return 1 + countNode(root.left) + countNode(root.right)


def heightDFS(root):
    """Height via recursion = 1 + max(left height, right height)."""
    if root is None:
        return 0
    return 1 + max(heightDFS(root.left), heightDFS(root.right))


def sumNode(root):
    """Sum of all values = self + left subtree sum + right subtree sum."""
    if root is None:
        return 0
    return root.val + sumNode(root.left) + sumNode(root.right)


# ---- Diameter of a binary tree --------------------------------------------
# The longest path may NOT pass through the root, so at every node we ask:
#   "what is the longest path that bends at THIS node?" = leftHeight + rightHeight
# We keep a running max in a list (ans[0]) because ints are immutable and a
# plain int wouldn't carry the update back up the recursion.
def height(root, ans):
    if root is None:
        return 0
    lh = height(root.left, ans)
    rh = height(root.right, ans)
    ans[0] = max(ans[0], lh + rh)       # best path bending at this node
    return 1 + max(lh, rh)              # normal height for the parent


def diameter(root):
    ans = [0]                           # mutable box so recursion can update it
    height(root, ans)
    return ans[0]                       # counted in NODES (use ans[0]-1 for edges)


def heightBFS(root):
    """Height by counting levels in a BFS. Returns 0 for an empty tree."""
    if root is None:
        return 0
    max_height = 0
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for _ in range(level_size):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        max_height += 1
    return max_height


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

    print("height (BFS):        ", heightBFS(root))
    print("height (DFS):        ", heightDFS(root))
    print("count of nodes:      ", countNode(root))
    print("sum of nodes:        ", sumNode(root))
    print("diameter (in nodes): ", diameter(root))


if __name__ == "__main__":
    main()
