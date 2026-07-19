# Serialize and Deserialize Binary Tree
#
# LeetCode: 297
# Difficulty: Hard
# Pattern: Serialize / deserialize
#
# Problem:
# Serialization is the process of converting a data structure or object into a sequence of
# bits so that it can be stored in a file or memory buffer, or transmitted across a network
# connection link to be reconstructed later in the same or another computer environment.
#
# Design an algorithm to serialize and deserialize a binary tree. There is no restriction on
# how your serialization/deserialization algorithm should work. You just need to ensure that
# a binary tree can be serialized to a string and this string can be deserialized to the
# original tree structure.
#
# Example 1:
# Input: root = [1, 2, 3, null, null, 4, 5]
# Output: [1, 2, 3, null, null, 4, 5]
#
# Example 2:
# Input: root = []
# Output: []
#
# Constraints:
# - The number of nodes in the tree is in the range [0, 10^4]
# - -1000 <= Node.val <= 1000

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Codec:
    def serialize(self, root):
        pass

    def deserialize(self, data):
        pass


if __name__ == '__main__':
    root = TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4), TreeNode(5)))
    codec = Codec()
    data = codec.serialize(root)
    ans = codec.deserialize(data)
    print(data, ans)
