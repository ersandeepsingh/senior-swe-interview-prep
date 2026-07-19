# Surrounded Regions
#
# LeetCode: 130
# Difficulty: Medium
# Pattern: Flood fill / region
#
# Problem:
# You are given an m x n matrix board containing letters 'X' and 'O', capture regions that
# are surrounded:
#
# Connect: A cell is connected to adjacent cells horizontally or vertically.
# Region: To form a region connect every 'O' cell.
# Surround: The region is surrounded with 'X' cells if you cannot reach the edge of the
# board from that region by connecting 'O' cells.
#
# A surrounded region is captured by replacing all 'O's with 'X's in that surrounded region.
#
# Example 1:
# Input: board = [["X","X","X","X"],["X","O","O","X"],["X","X","O","X"],["X","O","X","X"]]
# Output: [["X","X","X","X"],["X","X","X","X"],["X","X","X","X"],["X","O","X","X"]]
#
# Constraints:
# - m == board.length
# - n == board[i].length
# - 1 <= m, n <= 200
# - board[i][j] is 'X' or 'O'

def solve(board):
    pass


if __name__ == '__main__':
    board = [
        ["X", "X", "X", "X"],
        ["X", "O", "O", "X"],
        ["X", "X", "O", "X"],
        ["X", "O", "X", "X"],
    ]
    solve(board)
    print(board)
