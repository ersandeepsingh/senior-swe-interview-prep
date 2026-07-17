# 3Sum
#
# LeetCode: 15
# Difficulty: Medium
# Pattern: Triplets / k-sum
#
# Problem:
# Given an integer array nums, return all unique triplets
# [nums[i], nums[j], nums[k]] such that:
# - i, j, and k are distinct indices
# - nums[i] + nums[j] + nums[k] == 0
#
# The solution set must not contain duplicate triplets.
# The order of triplets and the order of elements inside each triplet do not
# matter.
#
# Example 1:
# Input: nums = [-1, 0, 1, 2, -1, -4]
# Output: [[-1, -1, 2], [-1, 0, 1]]
# Explanation:
# The distinct triplets that sum to 0 are [-1, -1, 2] and [-1, 0, 1].
#
# Example 2:
# Input: nums = [0, 1, 1]
# Output: []
# Explanation: The only possible triplet does not sum to 0.
#
# Example 3:
# Input: nums = [0, 0, 0]
# Output: [[0, 0, 0]]
# Explanation: The only possible triplet sums to 0.
#
# Constraints:
# - 3 <= nums.length <= 3000
# - -10^5 <= nums[i] <= 10^5
