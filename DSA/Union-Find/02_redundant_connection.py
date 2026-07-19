# Redundant Connection
#
# LeetCode: 684
# Difficulty: Medium
# Pattern: Redundant edge
#
# Problem:
# In this problem, a tree is an undirected graph that is connected and has no cycles.
#
# You are given a graph that started as a tree with n nodes labeled from 1 to n, with one
# additional edge added. The added edge has two different vertices chosen from 1 to n, and
# was not an edge that already existed. The resulting graph is given as a 2D array of edges.
# Each element of edges is a pair [u_i, v_i] that represents an undirected edge connecting
# nodes u_i and v_i.
#
# Return an edge that can be removed so that the resulting graph is a tree of n nodes.
# If there are multiple answers, return the answer that occurs last in the input.
#
# Example 1:
# Input: edges = [[1, 2], [1, 3], [2, 3]]
# Output: [2, 3]
#
# Example 2:
# Input: edges = [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]
# Output: [1, 4]
#
# Constraints:
# - n == edges.length
# - 3 <= n <= 1000
# - edges[i].length == 2
# - 1 <= u_i < v_i <= edges.length
# - u_i != v_i
# - There are no self-loops or repeated edges
# - The given graph is connected

def find_redundant_connection(edges):
    pass


if __name__ == '__main__':
    edges = [[1, 2], [1, 3], [2, 3]]
    ans = find_redundant_connection(edges)
    print(ans)
