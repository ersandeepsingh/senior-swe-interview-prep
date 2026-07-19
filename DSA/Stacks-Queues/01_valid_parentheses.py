# Valid Parentheses
#
# LeetCode: 20
# Difficulty: Easy
# Pattern: Balanced brackets
#
# Problem:
# Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine
# if the input string is valid.
#
# An input string is valid if:
# 1. Open brackets must be closed by the same type of brackets.
# 2. Open brackets must be closed in the correct order.
# 3. Every close bracket has a corresponding open bracket of the same type.
#
# Example 1:
# Input: s = "()"
# Output: True
#
# Example 2:
# Input: s = "()[]{}"
# Output: True
#
# Example 3:
# Input: s = "(]"
# Output: False
#
# Constraints:
# - 1 <= s.length <= 10^4
# - s consists of parentheses only '()[]{}'

def is_valid(s):
    pass


if __name__ == '__main__':
    s = "()[]{}"
    ans = is_valid(s)
    print(ans)
