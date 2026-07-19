# Path With Minimum Effort
#
# LeetCode: 1631
# Difficulty: Medium
# Pattern: Bellman-Ford / grid Dijkstra
#
# Problem:
# You are a hiker preparing for an upcoming hike. You are given heights, a 2D array of size
# rows x columns, where heights[row][col] represents the height of cell (row, col). You are
# situated in the top-left cell, (0, 0), and you hope to travel to the bottom-right cell,
# (rows-1, columns-1) (i.e., 0-indexed). You can move up, down, left, or right, and you wish
# to find a route that requires the minimum effort.
#
# A route's effort is the maximum absolute difference in heights between two consecutive
# cells of the route.
#
# Return the minimum effort required to travel from the top-left cell to the bottom-right cell.
#
# Example 1:
# Input: heights = [[1, 2, 2], [3, 8, 2], [5, 3, 5]]
# Output: 2
#
# Example 2:
# Input: heights = [[1, 2, 3], [3, 8, 4], [5, 3, 5]]
# Output: 1
#
# Example 3:
# Input: heights = [[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]
# Output: 0
#
# Constraints:
# - rows == heights.length
# - columns == heights[i].length
# - 1 <= rows, columns <= 100
# - 1 <= heights[i][j] <= 10^6

def minimum_effort_path(heights):
    pass


if __name__ == '__main__':
    heights = [[1, 2, 2], [3, 8, 2], [5, 3, 5]]
    ans = minimum_effort_path(heights)
    print(ans)
