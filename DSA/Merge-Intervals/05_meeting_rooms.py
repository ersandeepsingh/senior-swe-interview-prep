# Meeting Rooms
#
# LeetCode: 252
# Difficulty: Easy
# Pattern: Can-attend check
#
# Problem:
# Given an array of meeting time intervals where intervals[i] = [start_i, end_i],
# determine if a person could attend all meetings.
#
# Return True if a person can attend all meetings, otherwise return False.
#
# Example 1:
# Input: intervals = [[0, 30], [5, 10], [15, 20]]
# Output: False
# Explanation: There are overlapping meetings, so a person cannot attend all.
#
# Example 2:
# Input: intervals = [[7, 10], [2, 4]]
# Output: True
# Explanation: The meetings do not overlap.
#
# Constraints:
# - 0 <= intervals.length <= 10^4
# - intervals[i].length == 2
# - 0 <= start_i < end_i <= 10^6

def can_attend_meetings(intervals):
    pass


if __name__ == '__main__':
    intervals = [[0, 30], [5, 10], [15, 20]]
    ans = can_attend_meetings(intervals)
    print(ans)
