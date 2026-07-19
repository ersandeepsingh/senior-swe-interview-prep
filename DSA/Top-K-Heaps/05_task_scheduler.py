# Task Scheduler
#
# LeetCode: 621
# Difficulty: Medium
# Pattern: Scheduling with heap
#
# Problem:
# You are given an array of CPU tasks, each represented by letters A to Z, and a non-negative
# integer n that represents the cooldown period between two tasks with the same letter.
#
# Each cycle of the CPU consists of executing one task or being idle.
#
# Return the least number of cycles needed to finish all tasks.
#
# Example 1:
# Input: tasks = ["A", "A", "A", "B", "B", "B"], n = 2
# Output: 8
# Explanation: A -> B -> idle -> A -> B -> idle -> A -> B
#
# Example 2:
# Input: tasks = ["A", "C", "A", "B", "D", "B"], n = 1
# Output: 6
#
# Constraints:
# - 1 <= tasks.length <= 10^4
# - tasks[i] is an uppercase English letter
# - 0 <= n <= 100

def least_interval(tasks, n):
    pass


if __name__ == '__main__':
    tasks = ["A", "A", "A", "B", "B", "B"]
    n = 2
    ans = least_interval(tasks, n)
    print(ans)
