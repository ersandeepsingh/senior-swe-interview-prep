# Swap Nodes in Pairs
#
# LeetCode: 24
# Difficulty: Medium
# Pattern: Swap pairs
#
# Problem:
# Given a linked list, swap every two adjacent nodes and return its head.
# You must solve the problem without modifying the values in the list's nodes
# (i.e., only nodes themselves may be changed).
#
# Example 1:
# Input: head = [1, 2, 3, 4]
# Output: [2, 1, 4, 3]
#
# Example 2:
# Input: head = []
# Output: []
#
# Example 3:
# Input: head = [1]
# Output: [1]
#
# Example 4:
# Input: head = [1, 2, 3]
# Output: [2, 1, 3]
#
# Constraints:
# - The number of nodes in the list is in the range [0, 100]
# - 0 <= Node.val <= 100

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def swap_pairs(head):
    pass


if __name__ == '__main__':
    # head = [1, 2, 3, 4]
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
    ans = swap_pairs(head)
    print(ans)
