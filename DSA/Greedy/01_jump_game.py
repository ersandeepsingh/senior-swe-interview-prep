# Jump Game
#
# LeetCode: 55
# Difficulty: Medium
# Pattern: Jump / reachability
#
# Problem:
# You are given an integer array nums. You are initially positioned at the array's first index,
# and each element in the array represents your maximum jump length at that position.
#
# Return True if you can reach the last index, or False otherwise.
#
# Example 1:
# Input: nums = [2, 3, 1, 1, 4]
# Output: True
#
# Example 2:
# Input: nums = [3, 2, 1, 0, 4]
# Output: False
#
# Constraints:
# - 1 <= nums.length <= 10^4
# - 0 <= nums[i] <= 10^5

def can_jump(nums):
    # 'farthest' keeps track of the farthest index we can reach so far.
    farthest = 0
    # Iterate through each index in the array.
    for i in range(len(nums)):
        # If our current index is beyond the farthest we could jump to,
        # then we cannot reach this position, so return False.
        if i > farthest:
            return False
        # Update the farthest index we can reach from here.
        farthest = max(farthest, i + nums[i])
        # If at any point, our reach extends to the last index or beyond,
        # we can reach the end of the array, so return True.
        if farthest >= len(nums) - 1:
            return True
    # If we completed the loop, it means the last index is reachable.
    return True

if __name__ == '__main__':
    # nums = [2, 3, 1, 1, 4]
    nums = [3, 2, 1, 0, 4]
    ans = can_jump(nums)
    print(ans)
