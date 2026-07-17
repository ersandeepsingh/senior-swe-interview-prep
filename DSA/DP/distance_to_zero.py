# Given an m x n binary matrix mat, return a matrix where each cell contains the distance to the nearest 0.
# The distance between two adjacent cells is 1.
# You may only move in four directions: up, down, left, and right.
# Example:
# Input: mat = [[0,0,0],[0,1,0],[1,1,1]]
# Output:      [[0,0,0],[0,1,0],[1,2,1]]
# Constraints:
# - 1 <= mat.length, mat[0].length <= 50
# - 0 <= mat[i][j] <= 1
# - There is at least one 0 in mat.

import math


def update_matrix(mat):
    """
    Two-pass DP for shortest distance to nearest 0.

    A single top-left -> bottom-right pass only sees paths that go through
    top/left. Nearest 0 can also lie bottom/right, so we need a second pass
    from bottom-right -> top-left.

    State:
        dist[i][j] = min steps from (i, j) to any 0.
    """
    rows, cols = len(mat), len(mat[0])
    INF = math.inf

    # 0 stays 0; every other cell starts "unreachable" until a neighbor updates it.
    dist = [[0 if mat[i][j] == 0 else INF for j in range(cols)] for i in range(rows)]

    # Pass 1: top-left -> bottom-right. Use top and left neighbors only.
    for i in range(rows):
        for j in range(cols):
            if dist[i][j] == 0:
                continue
            top = dist[i - 1][j] if i > 0 else INF
            left = dist[i][j - 1] if j > 0 else INF
            dist[i][j] = min(dist[i][j], top + 1, left + 1)

    # Pass 2: bottom-right -> top-left. Use bottom and right neighbors.
    # This fills in shorter paths that were missed in pass 1.
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if dist[i][j] == 0:
                continue
            bottom = dist[i + 1][j] if i + 1 < rows else INF
            right = dist[i][j + 1] if j + 1 < cols else INF
            dist[i][j] = min(dist[i][j], bottom + 1, right + 1)

    return dist


if __name__ == "__main__":
    mat = [[0, 0, 0], [0, 1, 0], [1, 1, 1]]
    print(update_matrix(mat))
