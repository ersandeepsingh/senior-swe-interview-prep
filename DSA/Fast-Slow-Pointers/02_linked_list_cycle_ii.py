# Linked List Cycle II
#
# LeetCode: 142
# Difficulty: Medium
# Pattern: Cycle entry point
#
# Problem:
# Given the head of a linked list, return the node where the cycle begins.
# If there is no cycle, return None.
#
# There is a cycle in a linked list if there is some node in the list that can
# be reached again by continuously following the next pointer.
#
# Internally, pos is used to denote the index of the node that tail's next
# pointer is connected to (0-indexed). It is -1 if there is no cycle.
# Note that pos is not passed as a parameter.
#
# Do not modify the linked list.
#
# Example 1:
# Input: head = [3, 2, 0, -4], pos = 1
# Output: tail connects to node index 1
# Explanation:
# There is a cycle in the linked list, where tail connects to the node at
# index 1.
#
# Example 2:
# Input: head = [1, 2], pos = 0
# Output: tail connects to node index 0
# Explanation:
# There is a cycle in the linked list, where tail connects to the node at
# index 0.
#
# Example 3:
# Input: head = [1], pos = -1
# Output: no cycle
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


def detect_cycle(head):
    pass


if __name__ == '__main__':
    # head = [3, 2, 0, -4], pos = 1
    n0 = ListNode(3)
    n1 = ListNode(2)
    n2 = ListNode(0)
    n3 = ListNode(-4)
    n0.next, n1.next, n2.next, n3.next = n1, n2, n3, n1
    ans = detect_cycle(n0)
    print(ans)
