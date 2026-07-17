# Linked List Cycle
#
# LeetCode: 141
# Difficulty: Easy
# Pattern: Linked list cycle
#
# Problem:
# Given head, the head of a linked list, determine if the linked list has a
# cycle in it.
#
# There is a cycle in a linked list if there is some node in the list that can
# be reached again by continuously following the next pointer.
#
# Internally, pos is used to denote the index of the node that tail's next
# pointer is connected to. Note that pos is not passed as a parameter.
#
# Return True if there is a cycle in the linked list. Otherwise, return False.
#
# Example 1:
# Input: head = [3, 2, 0, -4], pos = 1
# Output: True
# Explanation:
# There is a cycle in the linked list, where the tail connects to the 1st node
# (0-indexed).
#
# Example 2:
# Input: head = [1, 2], pos = 0
# Output: True
# Explanation:
# There is a cycle in the linked list, where the tail connects to the 0th node.
#
# Example 3:
# Input: head = [1], pos = -1
# Output: False
# Explanation: There is no cycle in the linked list.
#
# Constraints:
# - The number of the nodes in the list is in the range [0, 10^4]
# - -10^5 <= Node.val <= 10^5
# - pos is -1 or a valid index in the linked-list

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def has_cycle(head):
    pass


if __name__ == '__main__':
    # head = [3, 2, 0, -4], pos = 1
    n0 = ListNode(3)
    n1 = ListNode(2)
    n2 = ListNode(0)
    n3 = ListNode(-4)
    n0.next, n1.next, n2.next, n3.next = n1, n2, n3, n1
    ans = has_cycle(n0)
    print(ans)
