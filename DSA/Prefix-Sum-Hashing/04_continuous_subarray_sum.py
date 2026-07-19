# Continuous Subarray Sum
#
# LeetCode: 523
# Difficulty: Medium
# Pattern: Prefix + divisibility
#
# Problem:
# Given an integer array nums and an integer k, return True if nums has a continuous subarray
# of size at least two whose elements sum up to a multiple of k, or False otherwise.
#
# An integer x is a multiple of k if there exists an integer n such that x = n * k.
# 0 is always a multiple of k.
#
# Example 1:
# Input: nums = [23, 2, 4, 6, 7], k = 6
# Output: True
#
# Example 2:
# Input: nums = [23, 2, 6, 4, 7], k = 6
# Output: True
#
# Example 3:
# Input: nums = [23, 2, 6, 4, 7], k = 13
# Output: False
#
# Constraints:
# - 1 <= nums.length <= 10^5
# - 0 <= nums[i] <= 10^9
# - 0 <= sum(nums[i]) <= 2^31 - 1
# - 1 <= k <= 2^31 - 1

def check_subarray_sum(nums, k):
    pass


if __name__ == '__main__':
    nums = [23, 2, 4, 6, 7]
    k = 6
    ans = check_subarray_sum(nums, k)
    print(ans)
