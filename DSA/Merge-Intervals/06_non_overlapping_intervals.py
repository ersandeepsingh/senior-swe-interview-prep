# Non-overlapping Intervals
#
# LeetCode: 435
# Difficulty: Medium
# Pattern: Non-overlap removal
#
# Problem:
# Given an array of intervals intervals where intervals[i] = [start_i, end_i],
# return the minimum number of intervals you need to remove to make the rest
# of the intervals non-overlapping.
#
# Note that intervals which only touch at a point are non-overlapping.
# For example, [1, 2] and [2, 3] are non-overlapping.
#
# Example 1:
# Input: intervals = [[1, 2], [2, 3], [3, 4], [1, 3]]
# Output: 1
# Explanation: [1, 3] can be removed and the rest of the intervals are
# non-overlapping.
#
# Example 2:
# Input: intervals = [[1, 2], [1, 2], [1, 2]]
# Output: 2
# Explanation: You need to remove two [1, 2] to make the rest of the intervals
# non-overlapping.
#
# Example 3:
# Input: intervals = [[1, 2], [2, 3]]
# Output: 0
# Explanation: You don't need to remove any of the intervals since they are
# already non-overlapping.
#
# Constraints:
# - 1 <= intervals.length <= 10^5
# - intervals[i].length == 2
# - -5 * 10^4 <= start_i < end_i <= 5 * 10^4

def erase_overlap_intervals(intervals):
    # If the list is empty or only one interval, no need to remove any interval
    if not intervals or len(intervals) == 1:
        return 0

    # Sort the intervals by their end time
    intervals.sort(key=lambda x: x[1])

    # Initialize the end of the last added interval to the end of the first interval
    end = intervals[0][1]
    count = 0  # Count of intervals to remove

    # Iterate over the intervals starting from the second
    for i in range(1, len(intervals)):
        # If the current interval overlaps with the previous, we need to remove one
        if intervals[i][0] < end:
            count += 1  # Increment removal count
        else:
            # If no overlap, update the end to the end of the current interval
            end = intervals[i][1]
    return count


if __name__ == '__main__':
    intervals = [[1, 2], [2, 3], [3, 4], [1, 3]]
    ans = erase_overlap_intervals(intervals)
    print(ans)
