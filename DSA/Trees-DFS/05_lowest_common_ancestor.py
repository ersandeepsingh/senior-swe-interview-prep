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
    pass


if __name__ == '__main__':
    p = TreeNode(5)
    q = TreeNode(1)
    root = TreeNode(3, p, q)
    ans = lowest_common_ancestor(root, p, q)
    print(ans)
