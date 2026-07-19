# Merge k Sorted Lists
#
# LeetCode: 23
# Difficulty: Hard
# Pattern: Merge sorted lists
#
# Problem:
# You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
#
# Merge all the linked-lists into one sorted linked-list and return it.
#
# Example 1:
# Input: lists = [[1, 4, 5], [1, 3, 4], [2, 6]]
# Output: [1, 1, 2, 3, 4, 4, 5, 6]
#
# Example 2:
# Input: lists = []
# Output: []
#
# Example 3:
# Input: lists = [[]]
# Output: []
#
# Constraints:
# - k == lists.length
# - 0 <= k <= 10^4
# - 0 <= lists[i].length <= 500
# - -10^4 <= lists[i][j] <= 10^4
# - lists[i] is sorted in ascending order
# - The sum of lists[i].length will not exceed 10^4

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_k_lists(lists):
    pass


if __name__ == '__main__':
    # lists = [[1, 4, 5], [1, 3, 4], [2, 6]]
    l1 = ListNode(1, ListNode(4, ListNode(5)))
    l2 = ListNode(1, ListNode(3, ListNode(4)))
    l3 = ListNode(2, ListNode(6))
    ans = merge_k_lists([l1, l2, l3])
    print(ans)
