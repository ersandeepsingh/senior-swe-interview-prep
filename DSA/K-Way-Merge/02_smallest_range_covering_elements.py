# Smallest Range Covering Elements from K Lists
#
# LeetCode: 632
# Difficulty: Hard
# Pattern: Smallest range across lists
#
# Problem:
# You have k lists of sorted integers in non-decreasing order. Find the smallest range that
# includes at least one number from each of the k lists.
#
# We define the range [a, b] is smaller than range [c, d] if b - a < d - c or
# a < c if b - a == d - c.
#
# Example 1:
# Input: nums = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]
# Output: [20, 24]
#
# Example 2:
# Input: nums = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
# Output: [1, 1]
#
# Constraints:
# - nums.length == k
# - 1 <= k <= 3500
# - 1 <= nums[i].length <= 50
# - -10^5 <= nums[i][j] <= 10^5
# - nums[i] is sorted in non-decreasing order

def smallest_range(nums):
    pass


if __name__ == '__main__':
    nums = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]
    ans = smallest_range(nums)
    print(ans)
