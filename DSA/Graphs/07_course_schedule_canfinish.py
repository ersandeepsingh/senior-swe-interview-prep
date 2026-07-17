# ============================================================
# COURSE SCHEDULE I  (LeetCode 207)  ->  "canFinish"
# ------------------------------------------------------------
# prerequisites[i] = [a, b] means: take b before a  (edge b -> a).
# You can finish all courses IFF the prerequisite graph has NO cycle.
# So this is just DIRECTED cycle detection (see 06_cycle_directed.py).
# ============================================================

from collections import deque


class Solution:
    def isCycle(self, source, visited, resPath, edges):
        visited[source] = True
        resPath[source] = True            # source is on the current path
        for i in range(len(edges)):
            v = edges[i][0]               # course that depends on...
            u = edges[i][1]               # ...this prerequisite
            if source == u:               # follow edge u -> v
                if not visited[v]:
                    visited[v] = True
                    if self.isCycle(v, visited, resPath, edges):
                        return True
                elif resPath[v]:          # v already on current path -> cycle
                    return True
        resPath[source] = False           # backtrack: off the current path
        return False

    def canFinish(self, numCourses, prerequisites):
        visited = [False] * numCourses
        resPath = [False] * numCourses
        for i in range(numCourses):
            if not visited[i]:
                if self.isCycle(i, visited, resPath, prerequisites):
                    return False          # a cycle means it's impossible
        return True

    
    #BFS
    def canFinishBFS(self, numCourses, prerequisites):
        queue = deque()
        result = []
        indegree = {i: 0 for i in range(numCourses)}
        # Build adjacency list for directed graph: adj_list[u] = [v, ...] (edges u -> v)
        adj_list = [[] for _ in range(numCourses)]
        for v, u in prerequisites:
            adj_list[u].append(v)
            indegree[v] += 1
        
        for i in range(len(indegree)):
            if indegree[i] == 0:
                queue.append(i)
        
        while queue:
            u = queue.popleft()
            result.append(u)
            for v in adj_list[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)
        if len(result) == numCourses:
            return True
        else:
            return False
                
            
            

if __name__ == '__main__':
    numCourses = 20
    prerequisites = [[0, 10], [3, 18], [5, 5], [6, 11],
                     [11, 14], [13, 1], [15, 1], [17, 4]]

    s = Solution()
    print("can finish all courses:", s.canFinish(numCourses, prerequisites))
    print("can finish all courses:", s.canFinishBFS(numCourses, prerequisites))
