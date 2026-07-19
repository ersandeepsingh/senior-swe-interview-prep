# Find K Pairs with Smallest Sums
#
# LeetCode: 373
# Difficulty: Medium
# Pattern: Kth smallest sum
#
# Problem:
# You are given two integer arrays nums1 and nums2 sorted in non-decreasing order and an
# integer k.
#
# Define a pair (u, v) which consists of one element from the first array and one element
# from the second array.
#
# Return the k pairs (u1, v1), (u2, v2), ..., (uk, vk) with the smallest sums.
#
# Example 1:
# Input: nums1 = [1, 7, 11], nums2 = [2, 4, 6], k = 3
# Output: [[1, 2], [1, 4], [1, 6]]
#
# Example 2:
# Input: nums1 = [1, 1, 2], nums2 = [1, 2, 3], k = 2
# Output: [[1, 1], [1, 1]]
#
# Constraints:
# - 1 <= nums1.length, nums2.length <= 10^5
# - -10^9 <= nums1[i], nums2[i] <= 10^9
# - nums1 and nums2 both are sorted in non-decreasing order
# - 1 <= k <= 10^4
# - k <= nums1.length * nums2.length

def k_smallest_pairs(nums1, nums2, k):
    pass


if __name__ == '__main__':
    nums1 = [1, 7, 11]
    nums2 = [2, 4, 6]
    k = 3
    ans = k_smallest_pairs(nums1, nums2, k)
    print(ans)
