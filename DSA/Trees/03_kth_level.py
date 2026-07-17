# ============================================================
# NODES AT THE K-th LEVEL
# ------------------------------------------------------------
# Walk down and decrement k each step. When k == 1 we are on the
# target level, so record the node. (Root is level 1.)
# ============================================================


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def kthlevel(root, k, res):
    if root is None:
        return
    if k == 1:                      # reached the target level
        res.append(root.val)
        return                      # no need to go deeper
    kthlevel(root.left, k - 1, res)
    kthlevel(root.right, k - 1, res)


def main():
    #         1                <- level 1
    #        / \
    #       2   3              <- level 2
    #      / \   \
    #     4   5   6            <- level 3
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    root.right.right = Node(6)

    res = []
    kthlevel(root, 3, res)
    print("Nodes at level 3:  ", res)


if __name__ == "__main__":
    main()
