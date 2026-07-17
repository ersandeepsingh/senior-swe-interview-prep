# ============================================================
# GRAPH BFS  (adjacency-MATRIX representation)
# ------------------------------------------------------------
# Same BFS logic as the adjacency-list version, but neighbours are
# found by scanning row `u` of the matrix: adj[u][i] == 1 means edge.
# Matrix costs O(V^2) space and each expansion scans V cells.
# ============================================================


def bfsTraversal(v, edges, start):
    # build V x V matrix, 1 = edge present (undirected -> fill both ways)
    adj = [[0 for _ in range(v)] for _ in range(v)]
    for a, b in edges:
        adj[a][b] = 1
        adj[b][a] = 1

    visited = [False] * v
    queue = []
    res = []
    # BUG FIX: was using the global `src` instead of the `start`
    # parameter. Now uses `start` so the function is self-contained.
    queue.append(start)
    visited[start] = True

    while queue:
        u = queue.pop(0)
        res.append(u)
        for i in range(v):                       # scan every possible neighbour
            if adj[u][i] == 1 and not visited[i]:
                queue.append(i)
                visited[i] = True
    return res


if __name__ == '__main__':
    v = 4
    edges = [[0, 1], [0, 2], [1, 3]]
    src = 0

    print("BFS (adjacency matrix) from vertex 0:")
    for x in bfsTraversal(v, edges, src):
        print(x, end=" ")
    print()
