# Given an array of intervals where intervals[i] = [starti, endi],
# merge all overlapping intervals, and return an array of the non-overlapping intervals 
# that cover all the intervals in the input.
# Example 1:

# Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
# Output: [[1,6],[8,10],[15,18]]
# Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].

def merge(intervals):
    intervals.sort(key=lambda x:x[0])
    result = []
    prev = intervals[0]
    for i in range(1,len(intervals)):
        if intervals[i][0] <= prev[1]:
            prev[1] = max(prev[1], intervals[i][1])
        else:
            result.append(prev)
            prev = intervals[i]
    result.append(prev)
    return result

# Alternative approach: Use a stack to merge the intervals after sorting.
def merge_with_stack(intervals):
    if not intervals:
        return []
    # Sort intervals based on the start value
    intervals.sort(key=lambda x: x[0])
    stack = []
    for interval in intervals:
        if not stack or stack[-1][1] < interval[0]:
            stack.append(interval[:])
        else:
            stack[-1][1] = max(stack[-1][1], interval[1])
    return stack

if __name__ == "__main__":
    intervals = [[1,3],[2,6],[8,10],[15,18]]
    merged = merge(intervals)
    print(merged)