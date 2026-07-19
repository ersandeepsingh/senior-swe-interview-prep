# Split Array Largest Sum
#
# LeetCode: 410
# Difficulty: Hard
# Pattern: Split / capacity minimization
#
# Problem:
# Given an integer array nums and an integer k, split nums into k non-empty subarrays
# such that the largest sum of any subarray is minimized.
#
# Return the minimized largest sum of the split.
#
# A subarray is a contiguous part of the array.
#
# Example 1:
# Input: nums = [7, 2, 5, 10, 8], k = 2
# Output: 18
# Explanation: There are four ways to split into two subarrays. Best is [7,2,5] and [10,8] with largest sum 18.
#
# Example 2:
# Input: nums = [1, 2, 3, 4, 5], k = 2
# Output: 9
#
# Constraints:
# - 1 <= nums.length <= 1000
# - 0 <= nums[i] <= 10^6
# - 1 <= k <= min(50, nums.length)

def split_array(nums, k):
    pass


if __name__ == '__main__':
    nums = [7, 2, 5, 10, 8]
    k = 2
    ans = split_array(nums, k)
    print(ans)
