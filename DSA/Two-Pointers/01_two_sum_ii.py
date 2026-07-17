# Two Sum II - Input Array Is Sorted
#
# LeetCode: 167
# Difficulty: Medium
# Pattern: Opposite ends (converging)
#
# Problem:
# Given a 1-indexed array of integers numbers that is already sorted in
# non-decreasing order, find two numbers such that they add up to a specific
# target number.
#
# Return the indices of the two numbers as a 1-indexed array [index1, index2].
#
# Rules:
# - There is exactly one solution.
# - You may not use the same element twice.
# - Use only constant extra space.
#
# Example 1:
# Input: numbers = [2, 7, 11, 15], target = 9
# Output: [1, 2]
# Explanation: 2 + 7 = 9, so the 1-indexed answer is [1, 2].
#
# Example 2:
# Input: numbers = [2, 3, 4], target = 6
# Output: [1, 3]
# Explanation: 2 + 4 = 6, so the 1-indexed answer is [1, 3].
#
# Example 3:
# Input: numbers = [-1, 0], target = -1
# Output: [1, 2]
# Explanation: -1 + 0 = -1, so the 1-indexed answer is [1, 2].
#
# Constraints:
# - 2 <= numbers.length <= 3 * 10^4
# - -1000 <= numbers[i] <= 1000
# - numbers is sorted in non-decreasing order
# - -1000 <= target <= 1000
# - Exactly one valid answer exists

def two_sum(numbers, target):
    pass


if __name__ == '__main__':
    numbers = [2, 7, 11, 15]
    target = 9
    ans = two_sum(numbers, target)
    print(ans)
