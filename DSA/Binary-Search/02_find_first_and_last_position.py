# Find First and Last Position of Element in Sorted Array
#
# LeetCode: 34
# Difficulty: Medium
# Pattern: Boundary / first-last
#
# Problem:
# Given an array of integers nums sorted in non-decreasing order, find the starting and
# ending position of a given target value.
#
# If target is not found in the array, return [-1, -1].
#
# You must write an algorithm with O(log n) runtime complexity.
#
# Example 1:
# Input: nums = [5, 7, 7, 8, 8, 10], target = 8
# Output: [3, 4]
#
# Example 2:
# Input: nums = [5, 7, 7, 8, 8, 10], target = 6
# Output: [-1, -1]
#
# Example 3:
# Input: nums = [], target = 0
# Output: [-1, -1]
#
# Constraints:
# - 0 <= nums.length <= 10^5
# - -10^9 <= nums[i] <= 10^9
# - nums is a non-decreasing array
# - -10^9 <= target <= 10^9

import re


def search_range(nums, target):
    left = 0
    right = len(nums)-1
    result = [-1,-1]
    while left <= right:
        mid = left + (right-left)//2
        if nums[mid] == target:
            break
        elif nums[mid] < target:
            left = mid+1
        else:
            right = mid-1
    # Ensure that target was actually found
    if nums[mid] != target:
        return [-1, -1]
    
    # Find the left boundary (first occurrence)
    l = mid
    while l - 1 >= 0 and nums[l - 1] == target:
        l -= 1
    result[0] = l

    # Find the right boundary (last occurrence)
    r = mid
    while r + 1 < len(nums) and nums[r + 1] == target:
        r += 1
    result[1] = r
    
    return result

if __name__ == '__main__':
    nums = [5, 7, 7, 8, 8, 10]
    target = 8
    ans = search_range(nums, target)
    print(ans)
