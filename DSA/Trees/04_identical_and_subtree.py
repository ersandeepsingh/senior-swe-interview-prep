# ============================================================
# IDENTICAL TREES  &  SUBTREE CHECK
# ------------------------------------------------------------
# identicalTrees(a, b) -> are two trees exactly the same?
# subTrees(sub, root)  -> is `sub` a subtree of `root`?
#                         (reuses identicalTrees as the building block)
# ============================================================


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def identicalTrees(a, b):
    if a is None and b is None:      # both empty -> identical
        return True
    if a is None or b is None:       # exactly one empty -> different
        return False
    return (a.val == b.val
            and identicalTrees(a.left, b.left)
            and identicalTrees(a.right, b.right))


def subTrees(sub, root):
    """True if `sub` matches some node of `root` and everything below it."""
    if root is None and sub is None:
        return True
    if root is None or sub is None:
        return False
    # If values match, try a full identical check anchored here...
    if sub.val == root.val and identicalTrees(sub, root):
        return True
    # ...otherwise keep searching in the left/right subtrees.
    return subTrees(sub, root.left) or subTrees(sub, root.right)


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

    # root2 is missing node 6, so NOT identical to root
    root2 = Node(1)
    root2.left = Node(2)
    root2.right = Node(3)
    root2.left.left = Node(4)
    root2.left.right = Node(5)

    # root3 is the (2 -> 4,5) subtree that DOES exist inside root
    root3 = Node(2)
    root3.left = Node(4)
    root3.right = Node(5)

    print("identical Trees:  ", identicalTrees(root, root2))
    print("is subtree:       ", subTrees(root3, root))


if __name__ == "__main__":
    main()
