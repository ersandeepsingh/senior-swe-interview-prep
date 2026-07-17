# ============================================================
# GRAPH DFS  (adjacency-MATRIX representation)
# ------------------------------------------------------------
# DFS where neighbours come from scanning row `u` of the matrix.
# ============================================================


def dfsHelper(u, v, visited, adj, res):
    for i in range(v):                       # scan every possible neighbour
        if adj[u][i] == 1 and not visited[i]:
            res.append(i)
            visited[i] = True
            dfsHelper(i, v, visited, adj, res)   # go deeper


def dfsTraversal(v, edges, start):
    adj = [[0 for _ in range(v)] for _ in range(v)]
    for a, b in edges:
        adj[a][b] = 1
        adj[b][a] = 1

    visited = [False] * v
    res = []
    visited[start] = True
    res.append(start)
    dfsHelper(start, v, visited, adj, res)
    return res


if __name__ == '__main__':
    v = 4
    edges = [[0, 1], [0, 2], [1, 3]]
    src = 0

    print("DFS (adjacency matrix) from vertex 0:")
    for x in dfsTraversal(v, edges, src):
        print(x, end=" ")
    print()
