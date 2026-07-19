# K Closest Points to Origin
#
# LeetCode: 973
# Difficulty: Medium
# Pattern: K closest
#
# Problem:
# Given an array of points where points[i] = [x_i, y_i] represents a point on the X-Y plane
# and an integer k, return the k closest points to the origin (0, 0).
#
# The distance between two points is the Euclidean distance.
#
# You may return the answer in any order. The answer is guaranteed to be unique.
#
# Example 1:
# Input: points = [[1, 3], [-2, 2]], k = 1
# Output: [[-2, 2]]
#
# Example 2:
# Input: points = [[3, 3], [5, -1], [-2, 4]], k = 2
# Output: [[3, 3], [-2, 4]]
#
# Constraints:
# - 1 <= k <= points.length <= 10^4
# - -10^4 <= x_i, y_i <= 10^4

def k_closest(points, k):
    pass


if __name__ == '__main__':
    points = [[1, 3], [-2, 2]]
    k = 1
    ans = k_closest(points, k)
    print(ans)
