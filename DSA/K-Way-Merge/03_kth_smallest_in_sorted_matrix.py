# Kth Smallest Element in a Sorted Matrix
#
# LeetCode: 378
# Difficulty: Medium
# Pattern: Kth smallest in matrix
#
# Problem:
# Given an n x n matrix where each of the rows and columns is sorted in ascending order,
# return the k-th smallest element in the matrix.
#
# Note that it is the k-th smallest element in the sorted order, not the k-th distinct element.
#
# You must find a solution with a memory complexity better than O(n^2).
#
# Example 1:
# Input: matrix = [[1, 5, 9], [10, 11, 13], [12, 13, 15]], k = 8
# Output: 13
#
# Example 2:
# Input: matrix = [[-5]], k = 1
# Output: -5
#
# Constraints:
# - n == matrix.length == matrix[i].length
# - 1 <= n <= 300
# - -10^9 <= matrix[i][j] <= 10^9
# - All the rows and columns of matrix are guaranteed to be sorted in non-decreasing order
# - 1 <= k <= n^2

def kth_smallest(matrix, k):
    pass


if __name__ == '__main__':
    matrix = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
    k = 8
    ans = kth_smallest(matrix, k)
    print(ans)
