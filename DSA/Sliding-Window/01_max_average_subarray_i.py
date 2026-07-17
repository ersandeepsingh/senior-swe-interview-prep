# Maximum Average Subarray I
#
# LeetCode: 643
# Difficulty: Easy
# Pattern: Fixed-size window
#
# Problem:
# You are given an integer array nums consisting of n elements, and an integer k.
#
# Find a contiguous subarray whose length is equal to k that has the maximum
# average value and return this value.
#
# Any answer with a calculation error less than 10^-5 will be accepted.
#
# Example 1:
# Input: nums = [1, 12, -5, -6, 50, 3], k = 4
# Output: 12.75000
# Explanation:
# Maximum average is (12 - 5 - 6 + 50) / 4 = 51 / 4 = 12.75
#
# Example 2:
# Input: nums = [5], k = 1
# Output: 5.00000
#
# Constraints:
# - n == nums.length
# - 1 <= k <= n <= 10^5
# - -10^4 <= nums[i] <= 10^4

def max_average_subarray(arr,k):
    max_avg = 0.0
    curr_sum = 0
    curr_avg = 0.0
    # Calculate the sum of the first window of size k
    for i in range(k):
        curr_sum += arr[i]         # Add each of the first k elements to curr_sum
    max_avg = curr_sum / k         # Initialize max_avg as the average of the first window
    for i in range(k, len(arr)):
        curr_sum = curr_sum + arr[i] - arr[i-k]
        curr_avg = curr_sum/k
        max_avg = max(curr_avg,max_avg)
    
    return max_avg

# Improved Version
def max_average_subarray_optimized(nums, k):
    """
    Space-efficient and idiomatic version to find the maximum average subarray of length k.
    Uses sliding window, computes running sum in O(n) time, with clear variable naming.
    """
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        if window_sum > max_sum:
            max_sum = window_sum
    return max_sum / k


if __name__ == '__main__':
    arr = [1, 12, -5, -6, 50, 3]
    k = 4
    ans = max_average_subarray(arr, k)
    print(f"Max average of array of length {k}-->", ans)