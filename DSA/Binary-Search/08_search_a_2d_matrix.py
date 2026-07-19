# Search a 2D Matrix
#
# LeetCode: 74
# Difficulty: Medium
# Pattern: 2D matrix search
#
# Problem:
# You are given an m x n integer matrix matrix with the following two properties:
# - Each row is sorted in non-decreasing order.
# - The first integer of each row is greater than the last integer of the previous row.
#
# Given an integer target, return True if target is in matrix or False otherwise.
#
# You must write a solution in O(log(m * n)) time complexity.
#
# Example 1:
# Input: matrix = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], target = 3
# Output: True
#
# Example 2:
# Input: matrix = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], target = 13
# Output: False
#
# Constraints:
# - m == matrix.length
# - n == matrix[i].length
# - 1 <= m, n <= 100
# - -10^4 <= matrix[i][j], target <= 10^4

def search_matrix(matrix, target):
    pass


if __name__ == '__main__':
    matrix = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    target = 3
    ans = search_matrix(matrix, target)
    print(ans)
