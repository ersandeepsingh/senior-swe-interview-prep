# Basic Calculator
#
# LeetCode: 224
# Difficulty: Hard
# Pattern: Basic calculator
#
# Problem:
# Given a string s representing a valid expression, implement a basic calculator to evaluate
# it, and return the result of the evaluation.
#
# Note: You are not allowed to use any built-in function which evaluates strings as
# mathematical expressions, such as eval().
#
# Example 1:
# Input: s = "1 + 1"
# Output: 2
#
# Example 2:
# Input: s = " 2-1 + 2 "
# Output: 3
#
# Example 3:
# Input: s = "(1+(4+5+2)-3)+(6+8)"
# Output: 23
#
# Constraints:
# - 1 <= s.length <= 3 * 10^5
# - s consists of digits, '+', '-', '(', ')', and ' '
# - s represents a valid expression
# - '+' is not used as a unary operation
# - '-' could be used as a unary operation
# - There will be no two consecutive operators in the input
# - Every number and running calculation will fit in a signed 32-bit integer

def calculate(s):
    pass


if __name__ == '__main__':
    s = "(1+(4+5+2)-3)+(6+8)"
    ans = calculate(s)
    print(ans)
