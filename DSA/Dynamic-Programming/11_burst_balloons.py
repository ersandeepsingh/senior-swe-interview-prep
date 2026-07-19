# Burst Balloons
#
# LeetCode: 312
# Difficulty: Hard
# Pattern: Interval DP
#
# Problem:
# You are given n balloons, indexed from 0 to n - 1. Each balloon is painted with a number
# on it represented by an array nums. You are asked to burst all the balloons.
#
# If you burst the i-th balloon, you will get nums[i - 1] * nums[i] * nums[i + 1] coins.
# If i - 1 or i + 1 goes out of bounds of the array, then treat it as if there is a balloon
# with a 1 painted on it.
#
# Return the maximum coins you can collect by bursting the balloons wisely.
#
# Example 1:
# Input: nums = [3, 1, 5, 8]
# Output: 167
#
# Example 2:
# Input: nums = [1, 5]
# Output: 10
#
# Constraints:
# - n == nums.length
# - 1 <= n <= 300
# - 0 <= nums[i] <= 100

def max_coins(nums):
    pass


if __name__ == '__main__':
    nums = [3, 1, 5, 8]
    ans = max_coins(nums)
    print(ans)
