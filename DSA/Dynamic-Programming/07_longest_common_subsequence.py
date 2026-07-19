# Longest Common Subsequence
#
# LeetCode: 1143
# Difficulty: Medium
# Pattern: LCS (2-string DP)
#
# Problem:
# Given two strings text1 and text2, return the length of their longest common subsequence.
# If there is no common subsequence, return 0.
#
# A subsequence of a string is a new string generated from the original string with some
# characters (can be none) deleted without changing the relative order of the remaining characters.
#
# Example 1:
# Input: text1 = "abcde", text2 = "ace"
# Output: 3
#
# Example 2:
# Input: text1 = "abc", text2 = "abc"
# Output: 3
#
# Example 3:
# Input: text1 = "abc", text2 = "def"
# Output: 0
#
# Constraints:
# - 1 <= text1.length, text2.length <= 1000
# - text1 and text2 consist of only lowercase English characters

def longest_common_subsequence(text1, text2):
    pass


if __name__ == '__main__':
    text1 = "abcde"
    text2 = "ace"
    ans = longest_common_subsequence(text1, text2)
    print(ans)
