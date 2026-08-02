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


import heapq


def min_meeting_rooms(intervals):
    # To solve this, we use a min-heap to keep track of end times of ongoing meetings.
    # Sort the intervals by start time (since we care when meetings begin).
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[0])
    # min_heap keeps the end time of meetings currently occupying rooms
    min_heap = []
    
    for interval in intervals:
        # If the room due to free up the earliest is free before the meeting starts, reuse it
        if min_heap and interval[0] >= min_heap[0]:
            heapq.heappop(min_heap)  # Remove the room that got free
        # Allocate a new room (heapq always pushes)
        heapq.heappush(min_heap, interval[1])
        # The heap size tells us the number of rooms occupied at this moment

    # The size of the heap is the min number of rooms needed for all meetings
    return len(min_heap)
        


if __name__ == '__main__':
    intervals = [[0, 30], [5, 10], [15, 20]]
    ans = min_meeting_rooms(intervals)
    print(ans)
