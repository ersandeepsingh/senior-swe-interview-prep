# Remove Duplicates from Sorted Array
#
# LeetCode: 26
# Difficulty: Easy
# Pattern: Same-direction (read/write)
#
# Problem:
# Given an integer array nums sorted in non-decreasing order, remove the
# duplicates in-place such that each unique element appears only once.
#
# The relative order of the elements should stay the same.
#
# Return the number of unique elements in nums.
#
# Let k be the number of unique elements. After processing:
# - The first k elements of nums should contain the unique elements in their
#   original order.
# - The elements after index k - 1 do not matter.
# - Return k.
#
# Example 1:
# Input: nums = [1, 1, 2]
# Output: 2, nums = [1, 2, _]
# Explanation:
# The function should return k = 2, and the first two elements of nums should
# be 1 and 2.
#
# Example 2:
# Input: nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
# Output: 5, nums = [0, 1, 2, 3, 4, _, _, _, _, _]
# Explanation:
# The function should return k = 5, and the first five elements should be
# 0, 1, 2, 3, and 4.
#
# Constraints:
# - 1 <= nums.length <= 3 * 10^4
# - -100 <= nums[i] <= 100
# - nums is sorted in non-decreasing order
