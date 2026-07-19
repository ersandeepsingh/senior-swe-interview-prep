# Course Schedule
#
# LeetCode: 207
# Difficulty: Medium
# Pattern: Ordering feasibility
#
# Problem:
# There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1.
# You are given an array prerequisites where prerequisites[i] = [a_i, b_i] indicates that you
# must take course b_i first if you want to take course a_i.
#
# Return True if you can finish all courses. Otherwise, return False.
#
# Example 1:
# Input: numCourses = 2, prerequisites = [[1, 0]]
# Output: True
#
# Example 2:
# Input: numCourses = 2, prerequisites = [[1, 0], [0, 1]]
# Output: False
#
# Constraints:
# - 1 <= numCourses <= 2000
# - 0 <= prerequisites.length <= 5000
# - prerequisites[i].length == 2
# - 0 <= a_i, b_i < numCourses
# - All the pairs prerequisites[i] are unique

# It uses Kahn's algorithm (BFS approach) to detect cycles in a directed graph by keeping track of in-degrees.
# If the number of nodes processed in topological order equals num_courses, all courses can be finished (no cycle). 
# Otherwise, there is a cycle, making it impossible.
def can_finish(num_courses, prerequisites):
    adj_list = [[] for i in range(num_courses)]
    for u,v in prerequisites:
        adj_list[u].append(v)
    in_degree = [0 for i in range(num_courses)]
    print(adj_list)
    for i in range(len(adj_list)):
        for val in adj_list[i]:
            in_degree[val] += 1
    queue = []
    result = []
    for i in range(len(in_degree)):
        if in_degree[i]==0:
            queue.append(i)
    while queue:
        u = queue.pop(0)
        result.append(u)
        for v in adj_list[u]:
            in_degree[v] -=1
            if in_degree[v]==0:
                queue.append(v)
    print(result)
    return True if len(result) == num_courses else False


if __name__ == '__main__':
    # Bigger example to test
    num_courses = 6
    prerequisites = [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]]
    ans = can_finish(num_courses, prerequisites)
    print(ans)  # Expect True

    # Add also a cycle to check return False
    num_courses2 = 4
    prerequisites2 = [[1,0], [2,1], [3,2], [1,3]]
    ans2 = can_finish(num_courses2, prerequisites2)
    print(ans2)  # Expect False
