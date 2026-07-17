# Reverse Even-Indexed Nodes and Append
# Given a singly linked list, extract all even-indexed nodes, reverse their order, and append them to the end of the list in one traversal. Return the head of the modified list.

# Example

# Input

# head = [10, 20, 30, 40, 50, 60]
# Output

# [20, 40, 60, 50, 30, 10]

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_even_indexed_and_append(head):
    if not head or not head.next:  # 0 or 1 node
        return head

    even_nodes = None          # Stack of even-indexed nodes (reversed order)
    odd_head = odd_tail = None  # Odd-indexed list, kept in original order
    curr = head
    idx = 0  # 0-indexed: node 0 is the first "even" node

    # Single pass, no dummy node and no new allocations.
    while curr:
        nxt = curr.next
        if idx % 2 == 0:
            # Push onto the even stack (reverses order automatically)
            curr.next = even_nodes
            even_nodes = curr
        else:
            # Append to the tail of the odd list
            if odd_tail is None:
                odd_head = curr
            else:
                odd_tail.next = curr
            odd_tail = curr
            curr.next = None
        curr = nxt
        idx += 1

    # Attach the reversed even nodes after the odd list
    odd_tail.next = even_nodes
    return odd_head

# Helper functions for demonstration
def build_linked_list(lst):
    dummy = ListNode(0)
    curr = dummy
    for val in lst:
        curr.next = ListNode(val)
        curr = curr.next
    return dummy.next

def linked_list_to_list(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result

# Example usage:
if __name__ == "__main__":
    data = [10, 20, 30, 40, 50, 60]
    head = build_linked_list(data)
    new_head = reverse_even_indexed_and_append(head)
    print(linked_list_to_list(new_head))  # Output: [20, 40, 60, 50, 30, 10]