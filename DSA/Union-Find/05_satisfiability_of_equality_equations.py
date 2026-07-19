# Satisfiability of Equality Equations
#
# LeetCode: 990
# Difficulty: Medium
# Pattern: Equations consistency
#
# Problem:
# You are given an array of strings equations that represent relationships between variables
# where each string equations[i] is of length 4 and takes one of two different forms:
# "a==b" or "a!=b". Here, a and b are lowercase letters (not necessarily different) that
# represent one-letter variable names.
#
# Return True if it is possible to assign integers to variable names so as to satisfy all
# the given equations, or False otherwise.
#
# Example 1:
# Input: equations = ["a==b", "b!=a"]
# Output: False
#
# Example 2:
# Input: equations = ["b==a", "a==b"]
# Output: True
#
# Constraints:
# - 1 <= equations.length <= 500
# - equations[i].length == 4
# - equations[i][0] and equations[i][3] are lowercase letters
# - equations[i][1] is either '=' or '!'
# - equations[i][2] is '='

def equations_possible(equations):
    pass


if __name__ == '__main__':
    equations = ["a==b", "b!=a"]
    ans = equations_possible(equations)
    print(ans)
