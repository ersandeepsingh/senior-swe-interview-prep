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
    # 1. Initialize low = 0, mid = 0, high = len(nums) - 1.
    # 2. While mid <= high:
    #    - If nums[mid] == 0:
    #          swap nums[low] and nums[mid], increment low and mid.
    #    - If nums[mid] == 1:
    #          just increment mid.
    #    - If nums[mid] == 2:
    #          swap nums[mid] and nums[high], decrement high.
    #
    # This one-pass approach sorts the colors in-place with constant space.
    low = 0
    mid = 0
    high = len(nums) - 1
    while mid<=high:
        if nums[mid] == 0:
            nums[mid], nums[low] = nums[low], nums[mid]
            low+=1
            mid+=1
        elif nums[mid] == 1:
            mid+=1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high-=1

if __name__ == '__main__':
    nums = [2, 0, 2, 1, 1, 0]
    sort_colors(nums)
    print(nums)
