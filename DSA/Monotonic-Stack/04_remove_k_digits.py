# Remove K Digits
#
# LeetCode: 402
# Difficulty: Medium
# Pattern: Remove to keep monotonic
#
# Problem:
# Given string num representing a non-negative integer num, and an integer k, return the
# smallest possible integer after removing k digits from num.
#
# Example 1:
# Input: num = "1432219", k = 3
# Output: "1219"
#
# Example 2:
# Input: num = "10200", k = 1
# Output: "200"
#
# Example 3:
# Input: num = "10", k = 2
# Output: "0"
#
# Constraints:
# - 1 <= k <= num.length <= 10^5
# - num consists of only digits
# - num does not have any leading zeros except for the zero itself

def remove_kdigits(num, k):
    pass


if __name__ == '__main__':
    num = "1432219"
    k = 3
    ans = remove_kdigits(num, k)
    print(ans)
