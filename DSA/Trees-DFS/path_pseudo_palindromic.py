# Given the root of a binary tree, return the number of root-to-leaf paths where, if you take all the node values along the path, they can be rearranged to form a palindrome. 
# In such a path, at most one value can occur an odd number of times.
#
# Example:
#         2
#        / \
#       3   1
#      / \   \
#     3   1   1
#
# Output: 2
# Explanation: There are two pseudo-palindromic paths:
# - 2 → 3 → 3
# - 2 → 1 → 1
# Both paths can be rearranged to form a palindrome.


def pseudo_palindrome(root):
    freq = {}
    def dfs(node):
        if not node:
            return 0
         # Choose
        freq[node.val] = freq.get(node.val, 0) + 1

        count = 0

        if not node.left and not node.right:
            odd_count = 0

            for frequency in freq.values():
                if frequency % 2 == 1:
                    odd_count += 1

            if odd_count <= 1:
                count = 1

        else:
            # Explore
            count += dfs(node.left)
            count += dfs(node.right)

        # Undo
        freq[node.val] -= 1
    dfs(root)