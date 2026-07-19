# Binary Tree Right Side View
#
# LeetCode: 199
# Difficulty: Medium
# Pattern: Right side view
#
# Problem:
# Given the root of a binary tree, imagine yourself standing on the right side of it,
# return the values of the nodes you can see ordered from top to bottom.
#
# Example 1:
# Input: root = [1, 2, 3, null, 5, null, 4]
# Output: [1, 3, 4]
#
# Example 2:
# Input: root = [1, null, 3]
# Output: [1, 3]
#
# Example 3:
# Input: root = []
# Output: []
#
# Constraints:
# - The number of nodes in the tree is in the range [0, 100]
# - -100 <= Node.val <= 100

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def right_side_view(root):
    pass


if __name__ == '__main__':
    root = TreeNode(1, TreeNode(2, None, TreeNode(5)), TreeNode(3, None, TreeNode(4)))
    ans = right_side_view(root)
    print(ans)
