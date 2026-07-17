# Sort Colors
#
# LeetCode: 75
# Difficulty: Medium
# Pattern: Partitioning (Dutch flag)
#
# Problem:
# Given an array nums with n objects colored red, white, or blue, sort them
# in-place so that objects of the same color are adjacent, with the colors in
# the order red, white, and blue.
#
# The integers represent colors as follows:
# - 0 means red
# - 1 means white
# - 2 means blue
#
# You must solve this problem without using the library's sort function.
#
# Follow-up:
# Could you solve it in one pass using only constant extra space?
#
# Example 1:
# Input: nums = [2, 0, 2, 1, 1, 0]
# Output: [0, 0, 1, 1, 2, 2]
#
# Example 2:
# Input: nums = [2, 0, 1]
# Output: [0, 1, 2]
#
# Example 3:
# Input: nums = [0]
# Output: [0]
#
# Constraints:
# - n == nums.length
# - 1 <= n <= 300
# - nums[i] is either 0, 1, or 2

def sort_colors(nums):
    pass


if __name__ == '__main__':
    nums = [2, 0, 2, 1, 1, 0]
    sort_colors(nums)
    print(nums)
