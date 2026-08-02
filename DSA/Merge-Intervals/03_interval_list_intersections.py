# Interval List Intersections
#
# LeetCode: 986
# Difficulty: Medium
# Pattern: Interval intersection
#
# Problem:
# You are given two lists of closed intervals, firstList and secondList, where
# firstList[i] = [start_i, end_i] and secondList[j] = [start_j, end_j].
# Each list of intervals is pairwise disjoint and in sorted order.
#
# Return the intersection of these two interval lists.
#
# A closed interval [a, b] (with a <= b) denotes the set of real numbers x
# with a <= x <= b.
#
# The intersection of two closed intervals is a set of real numbers that are
# either empty or represented as a closed interval. For example, the
# intersection of [1, 3] and [2, 4] is [2, 3].
#
# Example 1:
# Input: firstList = [[0, 2], [5, 10], [13, 23], [24, 25]],
#        secondList = [[1, 5], [8, 12], [15, 24], [25, 26]]
# Output: [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]
#
# Example 2:
# Input: firstList = [[1, 3], [5, 9]], secondList = []
# Output: []
#
# Constraints:
# - 0 <= firstList.length, secondList.length <= 1000
# - firstList.length + secondList.length >= 1
# - 0 <= start_i < end_i <= 10^9
# - end_i < start_{i+1}
# - 0 <= start_j < end_j <= 10^9
# - end_j < start_{j+1}

def interval_intersection(first_list, second_list):
    first = second = 0
    length1 = len(first_list)
    # Hint: Use two pointers, one for each interval list. Move through both lists, finding the overlap (intersection) between the current intervals.
    # If there's an intersection, add it to the result. Always advance the pointer for the interval that ends first.
    length2 = len(second_list)
    result = []
    while first < length1 and second < length2:
        a_start, a_end = first_list[first]
        b_start, b_end = second_list[second]

        # Find the overlap between the two intervals
        start = max(a_start, b_start)
        end = min(a_end, b_end)

        # If they overlap, add to result
        if start <= end:
            result.append([start, end])

        # Advance the pointer for the interval that ends first
        if a_end < b_end:
            first += 1
        else:
            second += 1
    return result
 


if __name__ == '__main__':
    first_list = [[0, 2], [5, 10], [13, 23], [24, 25]]
    second_list = [[1, 5], [8, 12], [15, 24], [25, 26]]
    ans = interval_intersection(first_list, second_list)
    print(ans)
