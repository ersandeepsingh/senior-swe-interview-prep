# Non-overlapping Intervals
#
# LeetCode: 435
# Difficulty: Medium
# Pattern: Interval scheduling
#
# Problem:
# Given an array of intervals intervals where intervals[i] = [start_i, end_i], return the
# minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.
#
# Note that intervals which only touch at a point are non-overlapping.
#
# Example 1:
# Input: intervals = [[1, 2], [2, 3], [3, 4], [1, 3]]
# Output: 1
#
# Example 2:
# Input: intervals = [[1, 2], [1, 2], [1, 2]]
# Output: 2
#
# Example 3:
# Input: intervals = [[1, 2], [2, 3]]
# Output: 0
#
# Constraints:
# - 1 <= intervals.length <= 10^5
# - intervals[i].length == 2
# - -5 * 10^4 <= start_i < end_i <= 5 * 10^4

def erase_overlap_intervals(intervals):
    pass


if __name__ == '__main__':
    intervals = [[1, 2], [2, 3], [3, 4], [1, 3]]
    ans = erase_overlap_intervals(intervals)
    print(ans)
