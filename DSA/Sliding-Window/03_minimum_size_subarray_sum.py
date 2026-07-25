# Minimum Size Subarray Sum
#
# LeetCode: 209
# Difficulty: Medium
# Pattern: Variable window (shortest)
#
# Problem:
# Given an array of positive integers nums and a positive integer target,
# return the minimal length of a subarray whose sum is greater than or equal
# to target.
#
# If there is no such subarray, return 0 instead.
#
# Example 1:
# Input: target = 7, nums = [2, 3, 1, 2, 4, 3]
# Output: 2
# Explanation: The subarray [4, 3] has the minimal length under the problem
# constraint.
#
# Example 2:
# Input: target = 4, nums = [1, 4, 4]
# Output: 1
#
# Example 3:
# Input: target = 11, nums = [1, 1, 1, 1, 1, 1, 1, 1]
# Output: 0
#
# Constraints:
# - 1 <= target <= 10^9
# - 1 <= nums.length <= 10^5
# - 1 <= nums[i] <= 10^4
import math
def min_subarray_len(target, nums):
    if sum(nums)<target:
        return 0
    left = 0
    curr_sum = 0
    min_len = math.inf
    for right in range(len(nums)):
        curr_sum += nums[right]
        while curr_sum>=target:
            min_len = min(min_len, right-left+1)
            curr_sum -= nums[left]
            left += 1
    return min_len   
            

if __name__ == '__main__':
    target = 7
    nums = [2, 3, 1, 2, 4, 3]
    ans = min_subarray_len(target, nums)
    print(ans)
