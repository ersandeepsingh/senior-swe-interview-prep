# Find Root-to-Node Path
# Given the root of a binary tree and a target value, return the path from the root to the node with the target value as a list.
#
# If the node with target value does not exist, return an empty list.
#
# Example:
# Input: 
#   root = 
#           1
#          / \
#         2   3
#        / \
#       4   5
#   target = 5
# Output: [1, 2, 5]


def find_path(root, target):
    path = []
    
    def dfs(node):
        if not node:
            return
        path.append(node.val)
        if node.val == target:
            return True
        if dfs(node.left):
            return True
        if dfs(node.right):
            return True
        path.pop()
        return False
    
    dfs(root)
    return path
    