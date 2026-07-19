# Validate Binary Search Tree
#
# LeetCode: 98
# Difficulty: Medium
# Pattern: BST validation
#
# Problem:
# Given the root of a binary tree, determine if it is a valid binary search tree (BST).
#
# A valid BST is defined as follows:
# - The left subtree of a node contains only nodes with keys less than the node's key.
# - The right subtree of a node contains only nodes with keys greater than the node's key.
# - Both the left and right subtrees must also be binary search trees.
#
# Example 1:
# Input: root = [2, 1, 3]
# Output: True
#
# Example 2:
# Input: root = [5, 1, 4, null, null, 3, 6]
# Output: False
# Explanation: The root node's value is 5 but its right child's value is 4.
#
# Constraints:
# - The number of nodes in the tree is in the range [1, 10^4]
# - -2^31 <= Node.val <= 2^31 - 1

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def is_valid_bst(root):
    pass


if __name__ == '__main__':
    root = TreeNode(2, TreeNode(1), TreeNode(3))
    ans = is_valid_bst(root)
    print(ans)
