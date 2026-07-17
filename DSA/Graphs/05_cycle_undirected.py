# ============================================================
# CYCLE DETECTION in an UNDIRECTED graph
# ------------------------------------------------------------
# Key idea: while exploring, if we reach an already-visited node
# that is NOT the parent we came from, we've found a cycle.
# Provided both ways: DFS (recursion) and BFS (queue of (node, parent)).
# ============================================================


def detectCycleDFS(start, par, adj, v, visited):
    for i in range(v):
        if adj[start][i] == 1:
            if not visited[i]:
                visited[i] = True
                if detectCycleDFS(i, start, adj, v, visited):
                    return True
            elif i != par:               # visited AND not the parent -> cycle
                return True
    return False


def dfsTraversal(v, edges, start):
    adj = [[0 for _ in range(v)] for _ in range(v)]
    for x, y in edges:
        adj[x][y] = 1
        adj[y][x] = 1                     # undirected -> both directions

    visited = [False] * v
    visited[start] = True
    return detectCycleDFS(start, -1, adj, v, visited)


# BUG FIX: renamed from "bfsTravelsal" (typo) to bfsTraversal.
def bfsTraversal(v, edges, start):
    adj = [[0 for _ in range(v)] for _ in range(v)]
    for x, y in edges:
        adj[x][y] = 1
        adj[y][x] = 1

    visited = [False] * v
    visited[start] = True
    queue = [[start, -1]]                 # (node, parent)
    while queue:
        curr, par = queue.pop(0)
        for i in range(v):
            if adj[curr][i] == 1:
                if not visited[i]:
                    visited[i] = True
                    queue.append([i, curr])
                elif i != par:            # visited AND not the parent -> cycle
                    return True
    return False

# Adj List implementation
def detectCycleDFS_adjlist(node, parent, adj, visited):
    for neighbor in adj[node]:
        if not visited[neighbor]:
            visited[neighbor] = True
            if detectCycleDFS_adjlist(neighbor, node, adj, visited):
                return True
        elif neighbor != parent:
            return True
    return False


def dfsTraversal_adjlist(v, edges, start):
    # Build adjacency list
    adj = [[] for _ in range(v)]
    for x, y in edges:
        adj[x].append(y)
        adj[y].append(x)   # undirected

    visited = [False] * v
    visited[start] = True
    return detectCycleDFS_adjlist(start, -1, adj, visited)

# BFS cycle detection in undirected graph (adjacency list)
def bfsTraversal_adjlist(v, edges, start):
    # Build adjacency list
    adj = [[] for _ in range(v)]
    for x, y in edges:
        adj[x].append(y)
        adj[y].append(x)

    visited = [False] * v
    queue = [[start, -1]]  # (node, parent)
    visited[start] = True

    while queue:
        node, parent = queue.pop(0)
        for neighbor in adj[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                queue.append([neighbor, node])
            elif neighbor != parent:
                return True  # Found a cycle
    return False


if __name__ == '__main__':
    v = 5
    edges = [[0, 1], [0, 2], [1, 3], [3, 0]]   # 0-1-3-0 forms a cycle
    src = 0

    # print("cycle (DFS):", dfsTraversal(v, edges, src))
    print("cycle (BFS):", bfsTraversal(v, edges, src))
