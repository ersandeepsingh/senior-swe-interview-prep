# Container With Most Water
#
# LeetCode: 11
# Difficulty: Medium
# Pattern: Container / area
#
# Problem:
# You are given an integer array height of length n. There are n vertical lines
# drawn such that the two endpoints of the i-th line are (i, 0) and
# (i, height[i]).
#
# Find two lines that, together with the x-axis, form a container that holds
# the maximum amount of water.
#
# Return the maximum amount of water a container can store.
#
# Note:
# You may not slant the container.
#
# Example 1:
# Input: height = [1, 8, 6, 2, 5, 4, 8, 3, 7]
# Output: 49
# Explanation:
# The lines at indices 1 and 8 have heights 8 and 7.
# Width = 8 - 1 = 7
# Height = min(8, 7) = 7
# Area = 7 * 7 = 49
#
# Example 2:
# Input: height = [1, 1]
# Output: 1
# Explanation:
# Width = 1 and height = 1, so the maximum area is 1.
#
# Constraints:
# - n == height.length
# - 2 <= n <= 10^5
# - 0 <= height[i] <= 10^4
