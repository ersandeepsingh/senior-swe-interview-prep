# ============================================================
# TOPOLOGICAL SORT  (DFS-based)
# ------------------------------------------------------------
# Valid only for a DAG (directed acyclic graph). Idea: run DFS, and
# once a node has no more unvisited neighbours, PUSH it on a stack.
# The reversed stack (pop order) is a valid topological order,
# because a node is finished only after everything it points to.
# ============================================================


def topoSort(start, adj_list, visited, stack):
    visited[start] = True
    for i in adj_list.get(start, []):
        if not visited[i]:
            topoSort(i, adj_list, visited, stack)
    stack.append(start)                  # push AFTER children are done


if __name__ == '__main__':
    adjacency_list = {
        0: [1, 2],
        1: [2],
        2: [3],
        3: [4],
    }

    visited = [False] * (len(adjacency_list) + 1)
    stack = []
    for node in range(len(visited)):     # cover disconnected parts too
        if not visited[node]:
            topoSort(node, adjacency_list, visited, stack)

    print("Topological order (DFS):")
    while stack:
        print(stack.pop(), " ")          # reverse of finish order
