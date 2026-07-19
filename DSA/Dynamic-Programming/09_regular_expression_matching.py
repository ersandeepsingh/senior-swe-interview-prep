# Regular Expression Matching
#
# LeetCode: 10
# Difficulty: Hard
# Pattern: String matching / wildcards
#
# Problem:
# Given an input string s and a pattern p, implement regular expression matching with support
# for '.' and '*' where:
# - '.' Matches any single character.
# - '*' Matches zero or more of the preceding element.
#
# The matching should cover the entire input string (not partial).
#
# Example 1:
# Input: s = "aa", p = "a"
# Output: False
#
# Example 2:
# Input: s = "aa", p = "a*"
# Output: True
#
# Example 3:
# Input: s = "ab", p = ".*"
# Output: True
#
# Constraints:
# - 1 <= s.length <= 20
# - 1 <= p.length <= 20
# - s contains only lowercase English letters
# - p contains only lowercase English letters, '.', and '*'

def is_match(s, p):
    pass


if __name__ == '__main__':
    s = "aa"
    p = "a*"
    ans = is_match(s, p)
    print(ans)
