# ============================================================
# LOWEST COMMON ANCESTOR (LCA) of a binary tree
# ------------------------------------------------------------
# Return the deepest node that has both p and q in its subtree.
# Logic:
#   - if current node is p or q, it can itself be the answer -> return it
#   - recurse left and right
#   - if BOTH sides return something, THIS node is the split point (LCA)
#   - otherwise bubble up whichever side found a target
# Assumes both p and q actually exist in the tree.
# ============================================================
# NOTE: removed junk "from turtle import left" import (unused).


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def lca(root, p, q):
    if root is None:
        return None
    if root.val == p or root.val == q:  # found one of the targets
        return root

    leftlca = lca(root.left, p, q)
    rightlca = lca(root.right, p, q)

    if leftlca and rightlca:            # p and q live on opposite sides
        return root                     # -> this node is the LCA
    return leftlca if leftlca else rightlca


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

    p, q = 4, 5
    print("LCA of", p, "and", q, ": ", lca(root, p, q).val)  # -> 2


if __name__ == "__main__":
    main()
