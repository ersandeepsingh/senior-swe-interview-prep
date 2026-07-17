# ============================================================
# TOP VIEW  &  BOTTOM VIEW  (vertical / horizontal-distance based)
# ------------------------------------------------------------
# Idea: give every node a horizontal distance (hd):
#   root = 0,  left child = hd - 1,  right child = hd + 1
# Nodes sharing an hd form one vertical column.
#   TOP view    -> keep the FIRST node seen per column  (if hd not in hash)
#   BOTTOM view -> keep the LAST node seen per column   (always overwrite)
# Do a BFS so nodes are seen top-to-bottom, then read columns left->right
# by iterating sorted(hash) keys.
# ============================================================


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def topView(root):
    if root is None:
        return []
    queue = [(root, 0)]                 # (node, horizontal distance)
    hash = {}
    while queue:
        node, pos = queue.pop(0)
        if pos not in hash:             # only the topmost node per column
            hash[pos] = node.val
        if node.left:
            queue.append((node.left, pos - 1))
        if node.right:
            queue.append((node.right, pos + 1))
    # sorted(hash) gives columns left -> right (NOT insertion order)
    return [hash[pos] for pos in sorted(hash)]


def bottomView(root):
    if root is None:
        return []
    queue = [(root, 0)]
    hash = {}
    while queue:
        node, pos = queue.pop(0)
        hash[pos] = node.val            # overwrite -> lowest node per column wins
        if node.left:
            queue.append((node.left, pos - 1))
        if node.right:
            queue.append((node.right, pos + 1))
    return [hash[pos] for pos in sorted(hash)]


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

    print("Top View:    ", topView(root))     # [4, 2, 1, 3, 6]
    print("Bottom View: ", bottomView(root))  # [4, 2, 5, 3, 6]


if __name__ == "__main__":
    main()
