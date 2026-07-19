# Number of Islands II
#
# LeetCode: 305
# Difficulty: Hard
# Pattern: Grid islands (dynamic)
#
# Problem:
# You are given an empty 2D binary grid grid of size m x n. The grid represents a map where
# 0's represent water and 1's represent land. Initially, all the cells of grid are water cells
# (i.e., all the cells are 0's).
#
# We may perform an add land operation which turns the water at position into a land. You are
# given an array positions where positions[i] = [r_i, c_i] is the position (r_i, c_i) at which
# we should operate the i-th operation.
#
# Return an array of integers answer where answer[i] is the number of islands after turning
# the cell (r_i, c_i) into a land.
#
# Example 1:
# Input: m = 3, n = 3, positions = [[0, 0], [0, 1], [1, 2], [2, 1]]
# Output: [1, 1, 2, 3]
#
# Example 2:
# Input: m = 1, n = 1, positions = [[0, 0]]
# Output: [1]
#
# Constraints:
# - 1 <= m, n, positions.length <= 10^4
# - 1 <= m * n <= 10^4
# - positions[i].length == 2
# - 0 <= r_i < m
# - 0 <= c_i < n

def num_islands2(m, n, positions):
    pass


if __name__ == '__main__':
    m, n = 3, 3
    positions = [[0, 0], [0, 1], [1, 2], [2, 1]]
    ans = num_islands2(m, n, positions)
    print(ans)
