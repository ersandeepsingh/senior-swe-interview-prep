# Subarray Sum Equals K
#
# LeetCode: 560
# Difficulty: Medium
# Pattern: Subarray sum = k
#
# Problem:
# Given an array of integers nums and an integer k, return the total number of subarrays
# whose sum equals to k.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
# Example 1:
# Input: nums = [1, 1, 1], k = 2
# Output: 2
#
# Example 2:
# Input: nums = [1, 2, 3, -3], k = 3
# Output: 3
#
# Constraints:
# - 1 <= nums.length <= 2 * 10^4
# - -1000 <= nums[i] <= 1000
# - -10^7 <= k <= 10^7

def subarray_sum(nums, k):
    hash = {}
    count= 0
    prefix_sum = 0
    hash = {0: 1}
    for num in nums:
        prefix_sum += num
        count += hash.get(prefix_sum - k, 0)
        hash[prefix_sum] = hash.get(prefix_sum, 0) + 1
    return count

if __name__ == '__main__':
    nums = [1, 1, 1]
    k = 2
    ans = subarray_sum(nums, k)
    print(ans)
