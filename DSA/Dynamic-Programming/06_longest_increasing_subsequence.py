# Longest Increasing Subsequence
#
# LeetCode: 300
# Difficulty: Medium
# Pattern: LIS
#
# Problem:
# Given an integer array nums, return the length of the longest strictly increasing subsequence.
#
# Example 1:
# Input: nums = [10, 9, 2, 5, 3, 7, 101, 18]
# Output: 4
# Explanation: The longest increasing subsequence is [2, 3, 7, 101], therefore the length is 4.
#
# Example 2:
# Input: nums = [0, 1, 0, 3, 2, 3]
# Output: 4
#
# Example 3:
# Input: nums = [7, 7, 7, 7, 7, 7, 7]
# Output: 1
#
# Constraints:
# - 1 <= nums.length <= 2500
# - -10^4 <= nums[i] <= 10^4

def length_of_lis(nums):
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j]<nums[i]:
                dp[i] = max(dp[i],1+dp[j])
    
    return max(dp)
                
def print_lis(nums):
    #Prints one of the Longest Increasing Subsequences in nums.
    if not nums:
        print([])
        return

    n = len(nums)
    dp = [1] * n
    prev = [-1] * n

    # Fill dp[] and track predecessors for reconstruction
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                prev[i] = j

    # Find the index of the maximum value in dp[]
    lis_len = max(dp)
    lis_idx = dp.index(lis_len)

    # Reconstruct the LIS sequence
    seq = []
    while lis_idx != -1:
        seq.append(nums[lis_idx])
        lis_idx = prev[lis_idx]
    seq.reverse()
    print(seq)


if __name__ == '__main__':
    nums = [10, 9, 2, 5, 3, 7, 101, 18]
    ans = length_of_lis(nums)
    print(ans)
