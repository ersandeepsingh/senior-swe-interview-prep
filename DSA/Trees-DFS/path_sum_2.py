# Path Sum III
#
# LeetCode: 437
# Difficulty: Medium
# Pattern: Path Sum (Root Any, End Any, Down Only)
#
# Problem:
# Given the root of a binary tree and an integer targetSum, return the number of paths where the sum of the values along the path equals targetSum.
#
# The path does not need to start or end at the root or a leaf, but it must move only downward (from parent nodes to child nodes).
#
# Example:
#
#          10
#         /  \
#        5   -3
#       / \    \
#      3   2    11
#     / \   \
#    3  -2   1
#
# Input: root = [10,5,-3,3,2,null,11,3,-2,null,1], targetSum = 8
# Output: 3
# Explanation: The paths that sum to 8 are:
# 5 -> 3
# 5 -> 2 -> 1
# -3 -> 11


def path_sum(root, target):
    prefix_count = {0: 1}

    def dfs(node, current_sum):
        if not node:
            return 0

        current_sum += node.val

        # Number of valid paths ending at this node
        count = prefix_count.get(
            current_sum - target,
            0,
        )

        # Choose
        prefix_count[current_sum] = (
            prefix_count.get(current_sum, 0) + 1
        )

        # Explore
        count += dfs(node.left, current_sum)
        count += dfs(node.right, current_sum)

        # Undo
        prefix_count[current_sum] -= 1

        return count

    return dfs(root, 0)