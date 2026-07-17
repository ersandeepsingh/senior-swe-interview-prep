# Meeting Rooms II
#
# LeetCode: 253
# Difficulty: Medium
# Pattern: Min rooms / resources (sweep line)
#
# Problem:
# Given an array of meeting time intervals intervals where
# intervals[i] = [start_i, end_i], return the minimum number of conference
# rooms required.
#
# Example 1:
# Input: intervals = [[0, 30], [5, 10], [15, 20]]
# Output: 2
# Explanation:
# One meeting runs from 0 to 30.
# Another meeting runs from 5 to 10, overlapping with the first, so a second
# room is needed.
# The meeting from 15 to 20 also overlaps with the first meeting, so 2 rooms
# are required in total.
#
# Example 2:
# Input: intervals = [[7, 10], [2, 4]]
# Output: 1
# Explanation: The meetings do not overlap, so only 1 room is needed.
#
# Constraints:
# - 1 <= intervals.length <= 10^4
# - 0 <= start_i < end_i <= 10^6

def min_meeting_rooms(intervals):
    pass


if __name__ == '__main__':
    intervals = [[0, 30], [5, 10], [15, 20]]
    ans = min_meeting_rooms(intervals)
    print(ans)
