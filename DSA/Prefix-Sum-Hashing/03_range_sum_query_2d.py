# Range Sum Query 2D - Immutable
#
# LeetCode: 304
# Difficulty: Medium
# Pattern: 2D prefix
#
# Problem:
# Given a 2D matrix matrix, handle multiple queries of the following type:
# Calculate the sum of the elements of matrix inside the rectangle defined by its upper left
# corner (row1, col1) and lower right corner (row2, col2).
#
# Implement the NumMatrix class:
# - NumMatrix(int[][] matrix) Initializes the object with the integer matrix matrix.
# - int sumRegion(int row1, int col1, int row2, int col2) Returns the sum of the elements of
#   matrix inside the rectangle defined by its upper left corner (row1, col1) and lower right
#   corner (row2, col2).
#
# Example 1:
# Input:
# ["NumMatrix", "sumRegion", "sumRegion", "sumRegion"]
# [[[[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]], [2, 1, 4, 3], [1, 1, 2, 2], [1, 2, 2, 4]]
# Output: [null, 8, 11, 12]
#
# Constraints:
# - m == matrix.length
# - n == matrix[i].length
# - 1 <= m, n <= 200
# - -10^5 <= matrix[i][j] <= 10^5
# - 0 <= row1 <= row2 < m
# - 0 <= col1 <= col2 < n
# - At most 10^4 calls will be made to sumRegion

class NumMatrix:
    def __init__(self, matrix):
        pass

    def sum_region(self, row1, col1, row2, col2):
        pass


if __name__ == '__main__':
    matrix = [
        [3, 0, 1, 4, 2],
        [5, 6, 3, 2, 1],
        [1, 2, 0, 1, 5],
        [4, 1, 0, 1, 7],
        [1, 0, 3, 0, 5],
    ]
    num_matrix = NumMatrix(matrix)
    print(num_matrix.sum_region(2, 1, 4, 3))
    print(num_matrix.sum_region(1, 1, 2, 2))
    print(num_matrix.sum_region(1, 2, 2, 4))
