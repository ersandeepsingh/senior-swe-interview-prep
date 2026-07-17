# ============================================================
# COURSE SCHEDULE II  (LeetCode 210)  ->  "findOrder"
# ------------------------------------------------------------
# Return ONE valid order to take all courses, or [] if impossible.
# This is topological sort + cycle detection in one DFS:
#   - build the order by pushing finished nodes on a stack (like 08_)
#   - if we ever revisit a node on the current path -> cycle -> return []
# ============================================================


class Solution:
    def topoSort(self, s, visited, paths, edges, stack):
        visited[s] = True
        paths[s] = True                   # s on the current recursion path
        for i in range(len(edges)):
            u = edges[i][1]               # prerequisite
            v = edges[i][0]               # dependent course
            if u == s:                    # follow edge u -> v
                if not visited[v]:
                    if self.topoSort(v, visited, paths, edges, stack):
                        return True       # cycle found deeper
                elif paths[v]:            # v on current path -> cycle
                    return True
        paths[s] = False                  # backtrack
        stack.append(s)                   # finished -> add to order
        return False

    def findOrder(self, n, edges):
        visited = [False] * n
        paths = [False] * n
        stack = []
        for i in range(n):
            if not visited[i]:
                if self.topoSort(i, visited, paths, edges, stack):
                    return []             # cycle -> no valid ordering
        result = []
        while stack:
            result.append(stack.pop())    # reverse of finish order
        return result


if __name__ == '__main__':
    numCourses = 7
    prerequisites = [[1, 0], [0, 3], [0, 2], [3, 2],
                     [2, 5], [4, 5], [5, 6], [2, 4]]

    s = Solution()
    print("a valid course order:", s.findOrder(numCourses, prerequisites))
