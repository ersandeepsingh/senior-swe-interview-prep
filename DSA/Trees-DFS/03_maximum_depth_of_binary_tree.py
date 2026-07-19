# Maximum Depth of Binary Tree
#
# LeetCode: 104
# Difficulty: Easy
# Pattern: Depth / height
#
# Problem:
# Given the root of a binary tree, return its maximum depth.
#
# A binary tree's maximum depth is the number of nodes along the longest path from the
# root node down to the farthest leaf node.
#
# Example 1:
# Input: root = [3, 9, 20, null, null, 15, 7]
# Output: 3
#
# Example 2:
# Input: root = [1, null, 2]
# Output: 2
#
# Constraints:
# - The number of nodes in the tree is in the range [0, 10^4]
# - -100 <= Node.val <= 100

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_depth(root):
    pass


if __name__ == '__main__':
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    ans = max_depth(root)
    print(ans)
