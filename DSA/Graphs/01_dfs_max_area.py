# You are given an m x n binary matrix grid. An island is a group of 1's (representing land) 
# connected 4-directionally (horizontal or vertical.) You may assume all four edges of the grid 
# are surrounded by water.

# The area of an island is the number of cells with a value 1 in the island.

# Return the maximum area of an island in grid. If there is no island, return 0.

# # 

def maxAreaOfIsland(grid):
        m = len(grid)
        n = len(grid[0])
        def dfs(i,j):
            if i<0 and i>=m and j>=n and j<0 and grid[i][j] == 0:
                return 0
            return 1 + dfs(i-1,j) + dfs(i+1,j) + dfs(i,j+1) + dfs(i,j-1)
        max_area = 0
        visited = [[False]*n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                if not visited[i][j] and grid[i][j] == 1:
                    curr_area = dfs(i,j)
                    max_area = max(max_area,curr_area)
        return max_area
    
# Optimisation
def maxAreaOfIsland_optimized(grid):
    # Early returns or assignments
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    max_area = 0

    def dfs(x, y):
        # Out of bounds or already 0? Skip.
        if x < 0 or x >= m or y < 0 or y >= n or grid[x][y] == 0:
            return 0
        # Mark as visited by setting to 0.
        grid[x][y] = 0
        area = 1
        # Explore all four directions.
        for dx, dy in ((1,0),(0,1),(-1,0),(0,-1)):
            area += dfs(x+dx, y+dy)
        return area

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                area = dfs(i, j)
                max_area = max(max_area, area)
    return max_area
    
if __name__=='__main__':
    grid = [[0],[0]]
    maxAreaOfIsland(grid)