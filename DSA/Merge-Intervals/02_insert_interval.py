# Insert Interval
#
# LeetCode: 57
# Difficulty: Medium
# Pattern: Insert into sorted intervals
#
# Problem:
# You are given an array of non-overlapping intervals intervals where
# intervals[i] = [start_i, end_i] represent the start and the end of the i-th
# interval and intervals is sorted in ascending order by start_i.
#
# You are also given an interval newInterval = [start, end] that represents
# the start and end of another interval.
#
# Insert newInterval into intervals such that intervals is still sorted in
# ascending order by start_i and intervals still does not have any overlapping
# intervals (merge overlapping intervals if necessary).
#
# Return intervals after the insertion.
#
# Example 1:
# Input: intervals = [[1, 3], [6, 9]], newInterval = [2, 5]
# Output: [[1, 5], [6, 9]]
#
# Example 2:
# Input: intervals = [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]],
#        newInterval = [4, 8]
# Output: [[1, 2], [3, 10], [12, 16]]
# Explanation: Because the new interval [4, 8] overlaps with [3, 5], [6, 7],
# and [8, 10].
#
# Constraints:
# - 0 <= intervals.length <= 10^4
# - intervals[i].length == 2
# - 0 <= start_i <= end_i <= 10^5
# - intervals is sorted by start_i in ascending order
# - newInterval.length == 2
# - 0 <= start <= end <= 10^5
# Issues in the given code:
# 1. The logic for merging overlapping intervals is incorrect and can result in skipping intervals or index errors.
# 2. The code tries to manipulate the loop variable `i` inside the `for` loop, which does not affect the outer loop.
# 3. The 'pair' for merging intervals is always created inside the loop, potentially leading to appending incomplete/extra ranges.
# 4. The merged interval (`new_interval`) may not get inserted if its range is after all intervals.
# 5. The overlapping interval logic (`if intervals[i][1] > new_start:`) is not the correct check for overlap.
# 6. The main merge uses a while loop which can go out of bounds and doesn't have appropriate boundary conditions.
# 7. The function doesn't always add all intervals nor the (possibly merged) `new_interval` correctly.

# A correct approach is:
# - Add all intervals that come before `new_interval`.
# - Merge all that overlap with `new_interval`.
# - Add all intervals that come after.
#
# Here is the corrected code:

def insert(intervals, new_interval):
    result = []
    i = 0
    n = len(intervals)
    start, end = new_interval

    # 1. Add non-overlapping intervals before new_interval
    while i < n and intervals[i][1] < start:
        result.append(intervals[i])
        i += 1

    # 2. Merge all overlapping intervals with new_interval
    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    result.append([start, end])

    # 3. Add remaining intervals after new_interval
    while i < n:
        result.append(intervals[i])
        i += 1

    return result

if __name__ == '__main__':
    intervals = [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]],
    new_interval = [4, 8]
    ans = insert(intervals, new_interval)
    print(ans)
