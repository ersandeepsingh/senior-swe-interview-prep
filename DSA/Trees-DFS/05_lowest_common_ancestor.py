# Lowest Common Ancestor of a Binary Tree
#
# LeetCode: 236
# Difficulty: Medium
# Pattern: LCA
#
# Problem:
# Given a binary tree, find the lowest common ancestor (LCA) of two given nodes in the tree.
#
# According to the definition of LCA on Wikipedia: “The lowest common ancestor is defined
# between two nodes p and q as the lowest node in T that has both p and q as descendants
# (where we allow a node to be a descendant of itself).”
#
# Example 1:
# Input: root = [3, 5, 1, 6, 2, 0, 8, null, null, 7, 4], p = 5, q = 1
# Output: 3
#
# Example 2:
# Input: root = [3, 5, 1, 6, 2, 0, 8, null, null, 7, 4], p = 5, q = 4
# Output: 5
#
# Constraints:
# - The number of nodes in the tree is in the range [2, 10^5]
# - -10^9 <= Node.val <= 10^9
# - All Node.val are unique
# - p != q
# - p and q will exist in the tree

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        

def lowest_common_ancestor(root, p, q):
    if not root:
        return None

    if root.val == p or root.val == q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root

    return left if left else right

if __name__ == '__main__':
    # Build the example tree:
    #        3
    #      /   \
    #     5     1
    #    / \   / \
    #   6   2 0   8
    #      / \
    #     7   4

    n7 = TreeNode(7)
    n4 = TreeNode(4)
    n6 = TreeNode(6)
    n2 = TreeNode(2, n7, n4)
    n5 = TreeNode(5, n6, n2)
    n0 = TreeNode(0)
    n8 = TreeNode(8)
    n1 = TreeNode(1, n0, n8)
    root = TreeNode(3, n5, n1)

    # Example 1: LCA of 5 and 1 is 3
    print("LCA of 5 and 1:", lowest_common_ancestor(root, 5, 1).val)  # Output: 3
