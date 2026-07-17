# Reverse Linked List II
#
# LeetCode: 92
# Difficulty: Medium
# Pattern: Sub-list reversal
#
# Problem:
# Given the head of a singly linked list and two integers left and right where
# left <= right, reverse the nodes of the list from position left to position
# right, and return the reversed list.
#
# Example 1:
# Input: head = [1, 2, 3, 4, 5], left = 2, right = 4
# Output: [1, 4, 3, 2, 5]
#
# Example 2:
# Input: head = [5], left = 1, right = 1
# Output: [5]
#
# Constraints:
# - The number of nodes in the list is n
# - 1 <= n <= 500
# - -500 <= Node.val <= 500
# - 1 <= left <= right <= n
#
# Follow-up:
# Could you do it in one pass?

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverse_between(head, left, right):
    pass


if __name__ == '__main__':
    # head = [1, 2, 3, 4, 5], left = 2, right = 4
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5)))))
    left, right = 2, 4
    ans = reverse_between(head, left, right)
    print(ans)
