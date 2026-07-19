# Set Mismatch
#
# LeetCode: 645
# Difficulty: Easy
# Pattern: Set mismatch
#
# Problem:
# You have a set of integers s, which originally contains all the numbers from 1 to n.
# Unfortunately, due to some error, one of the numbers in s got duplicated to another
# number in the set, which results in repetition of one number and loss of another number.
#
# You are given an integer array nums representing the data status of this set after the error.
# Find the number that occurs twice and the number that is missing and return them as an array.
#
# Example 1:
# Input: nums = [1, 2, 2, 4]
# Output: [2, 3]
#
# Example 2:
# Input: nums = [1, 1]
# Output: [1, 2]
#
# Constraints:
# - 2 <= nums.length <= 10^4
# - 1 <= nums[i] <= 10^4

def find_error_nums(nums):
    pass


if __name__ == '__main__':
    nums = [1, 2, 2, 4]
    ans = find_error_nums(nums)
    print(ans)
