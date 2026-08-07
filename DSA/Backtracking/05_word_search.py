# Word Search
#
# LeetCode: 79
# Difficulty: Medium
# Pattern: Grid search / word
#
# Problem:
# Given an m x n grid of characters board and a string word, return True if word exists in
# the grid.
#
# The word can be constructed from letters of sequentially adjacent cells, where adjacent
# cells are horizontally or vertically neighboring. The same letter cell may not be used
# more than once.
#
# Example 1:
# Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
# Output: True
#
# Example 2:
# Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "SEE"
# Output: True
#
# Example 3:
# Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCB"
# Output: False
#
# Constraints:
# - m == board.length
# - n = board[i].length
# - 1 <= m, n <= 6
# - 1 <= word.length <= 15
# - board and word consist of only lowercase and uppercase English letters

def exist(board, word):
    rows = len(board)
    colums = len(board[0])
    visited = set()
    #explore each valid path using backtrack until we find the work 
    def backtrack(row, col, index):
        if index == len(word): # word found
            return True
        if row<0 or row >= rows or col<0 or col>=colums:
            return False
        
        if board[row][col] != word[index] or (row,col) in visited:
            return False
        
        visited.add((row,col))
        
        found = (backtrack(row-1,col,index+1) or
        backtrack(row+1,col,index+1) or
        backtrack(row,col-1,index+1) or
        backtrack(row,col+1,index+1) )
        
        visited.remove((row,col))
        return found
        
    for row in range(rows):
        for col in range(colums):
            if word[0] == board[row][col]:
                val = backtrack(row, col, 0)
                if val == True:
                    return True
    return False


if __name__ == '__main__':
    board = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
    word = "ABCCED"
    ans = exist(board, word)
    print(ans)
