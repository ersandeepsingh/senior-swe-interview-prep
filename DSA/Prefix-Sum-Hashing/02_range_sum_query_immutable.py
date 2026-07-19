# Range Sum Query - Immutable
#
# LeetCode: 303
# Difficulty: Easy
# Pattern: Range sum query
#
# Problem:
# Given an integer array nums, handle multiple queries of the following type:
# Calculate the sum of the elements of nums between indices left and right inclusive where
# left <= right.
#
# Implement the NumArray class:
# - NumArray(int[] nums) Initializes the object with the integer array nums.
# - int sumRange(int left, int right) Returns the sum of the elements of nums between indices
#   left and right inclusive (i.e. nums[left] + nums[left + 1] + ... + nums[right]).
#
# Example 1:
# Input:
# ["NumArray", "sumRange", "sumRange", "sumRange"]
# [[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]]
# Output: [null, 1, -1, -3]
#
# Constraints:
# - 1 <= nums.length <= 10^4
# - -10^5 <= nums[i] <= 10^5
# - 0 <= left <= right < nums.length
# - At most 10^4 calls will be made to sumRange

class NumArray:
    def __init__(self, nums):
        pass

    def sum_range(self, left, right):
        pass


if __name__ == '__main__':
    num_array = NumArray([-2, 0, 3, -5, 2, -1])
    print(num_array.sum_range(0, 2))
    print(num_array.sum_range(2, 5))
    print(num_array.sum_range(0, 5))
