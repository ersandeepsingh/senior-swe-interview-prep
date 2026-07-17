# ============================================================
# TOPOLOGICAL SORT  (BFS-based = Kahn's algorithm)
# ------------------------------------------------------------
# 1. Compute indegree (number of incoming edges) for every node.
# 2. Start with all indegree-0 nodes in a queue.
# 3. Pop a node, add to result, and "remove" it by decrementing the
#    indegree of its neighbours; any that hit 0 join the queue.
# Bonus: if the result has fewer nodes than the graph, a cycle exists.
# ============================================================


def topoSort(adj_list, queue):
    result = []
    indegree = {i: 0 for i in range(len(adj_list) + 1)}
    for _, neighbours in adj_list.items():
        for i in neighbours:
            indegree[i] += 1             # count incoming edges

    for i in range(len(indegree)):
        if indegree[i] == 0:             # no prerequisites -> ready first
            queue.append(i)

    while queue:
        curr = queue.pop(0)
        result.append(curr)
        for i in adj_list.get(curr, []):
            indegree[i] -= 1             # remove curr's outgoing edges
            if indegree[i] == 0:
                queue.append(i)
    return result


if __name__ == '__main__':
    adjacency_list = {
        0: [1, 2],
        1: [2],
        2: [3],
        3: [4],
    }

    queue = []
    print("Topological order (Kahn / BFS):")
    print(topoSort(adjacency_list, queue))
