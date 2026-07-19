# Find Median from Data Stream
#
# LeetCode: 295
# Difficulty: Hard
# Pattern: Streaming median (two heaps)
#
# Problem:
# The median is the middle value in an ordered integer list. If the size of the list is even,
# there is no middle value, and the median is the mean of the two middle values.
#
# Implement the MedianFinder class:
# - MedianFinder() initializes the MedianFinder object.
# - void addNum(int num) adds the integer num from the data stream to the data structure.
# - double findMedian() returns the median of all elements so far.
#
# Example 1:
# Input:
# ["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]
# [[], [1], [2], [], [3], []]
# Output: [null, null, null, 1.5, null, 2.0]
#
# Constraints:
# - -10^5 <= num <= 10^5
# - There will be at least one element in the data structure before calling findMedian
# - At most 5 * 10^4 calls will be made to addNum and findMedian

class MedianFinder:
    def __init__(self):
        pass

    def add_num(self, num):
        pass

    def find_median(self):
        pass


if __name__ == '__main__':
    mf = MedianFinder()
    mf.add_num(1)
    mf.add_num(2)
    print(mf.find_median())
    mf.add_num(3)
    print(mf.find_median())
