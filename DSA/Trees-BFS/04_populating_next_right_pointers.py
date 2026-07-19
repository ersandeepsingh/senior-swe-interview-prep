# Populating Next Right Pointers in Each Node
#
# LeetCode: 116
# Difficulty: Medium
# Pattern: Connect level pointers
#
# Problem:
# You are given a perfect binary tree where all leaves are on the same level, and every
# parent has two children. The binary tree has the following definition:
#
# struct Node {
#   int val;
#   Node *left;
#   Node *right;
#   Node *next;
# }
#
# Populate each next pointer to point to its next right node. If there is no next right
# node, the next pointer should be set to NULL.
#
# Initially, all next pointers are set to NULL.
#
# Example 1:
# Input: root = [1, 2, 3, 4, 5, 6, 7]
# Output: [1, #, 2, 3, #, 4, 5, 6, 7, #]
#
# Example 2:
# Input: root = []
# Output: []
#
# Constraints:
# - The number of nodes in the tree is in the range [0, 2^12 - 1]
# - -1000 <= Node.val <= 1000
# - The tree is a perfect binary tree

class Node:
    def __init__(self, val=0, left=None, right=None, next=None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next


def connect(root):
    pass


if __name__ == '__main__':
    root = Node(1, Node(2, Node(4), Node(5)), Node(3, Node(6), Node(7)))
    ans = connect(root)
    print(ans)
