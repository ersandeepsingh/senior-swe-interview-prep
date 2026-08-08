# Path Sum
#
# LeetCode: 112
# Difficulty: Easy
# Pattern: Path sum / root-to-leaf
#
# Problem:
# Given the root of a binary tree and an integer targetSum, return True if the tree has a
# root-to-leaf path such that adding up all the values along the path equals targetSum.
#
# A leaf is a node with no children.
#
# Example 1:
# Input: root = [5, 4, 8, 11, null, 13, 4, 7, 2, null, null, null, 1], targetSum = 22
# Output: True
#
# Example 2:
# Input: root = [1, 2, 3], targetSum = 5
# Output: False
#
# Example 3:
# Input: root = [], targetSum = 0
# Output: False
#
# Constraints:
# - The number of nodes in the tree is in the range [0, 5000]
# - -1000 <= Node.val <= 1000
# - -1000 <= targetSum <= 1000

from unittest import result


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def has_path_sum(root, target_sum):
    def dfs(node, remaining):
        if node == None:
            return
        remaining -= node.val
        if not node.left and not node.right:
            return remaining ==0
        
        return (dfs(node.left, remaining) or
            dfs(node.right, remaining))
    return dfs(root,target_sum)


def all_path_with_sum(root,target):
    result = []
    path = []
    def dfs(node, remaining):
        if node == None:
            return
        path.append(node.val)
        remaining -= node.val
        if not node.left and not node.right and remaining ==0:
                result.append(path.copy())
        dfs(node.left, remaining)
        dfs(node.right, remaining)
        path.pop()
    dfs(root,target)
    return result


    
if __name__ == '__main__':
    # root = [5, 4, 8, 11, null, 13, 4, 7, 2, null, null, null, 1], targetSum = 22
    root = TreeNode(5,
        TreeNode(4, TreeNode(11, TreeNode(7), TreeNode(2))),
        TreeNode(8, TreeNode(13), TreeNode(4, None, TreeNode(1))))
    target_sum = 22
    ans = has_path_sum(root, target_sum)
    paths = all_path_with_sum(root, target_sum)
    print(ans)
    print(paths)
