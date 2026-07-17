# Trapping Rain Water
#
# LeetCode: 42
# Difficulty: Hard
# Pattern: Trapping
#
# Problem:
# Given n non-negative integers representing an elevation map where the width
# of each bar is 1, compute how much water it can trap after raining.
#
# Water can be trapped above a bar only if there are taller or equal bars on
# both the left and right sides.
#
# Example 1:
# Input: height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
# Output: 6
# Explanation:
# The elevation map traps 6 units of rain water between the bars.
#
# Example 2:
# Input: height = [4, 2, 0, 3, 2, 5]
# Output: 9
# Explanation:
# Water is trapped between the taller bars on the left and right.
# The total trapped water is 9 units.
#
# Constraints:
# - n == height.length
# - 1 <= n <= 2 * 10^4
# - 0 <= height[i] <= 10^5

def trap(height):
    pass


if __name__ == '__main__':
    height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
    ans = trap(height)
    print(ans)
