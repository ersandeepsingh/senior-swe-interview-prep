# Course Schedule
#
# LeetCode: 207
# Difficulty: Medium
# Pattern: Cycle detection (directed)
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

def can_finish(num_courses, prerequisites):
    pass


if __name__ == '__main__':
    num_courses = 2
    prerequisites = [[1, 0]]
    ans = can_finish(num_courses, prerequisites)
    print(ans)
