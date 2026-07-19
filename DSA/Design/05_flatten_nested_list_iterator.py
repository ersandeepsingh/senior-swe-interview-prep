# Flatten Nested List Iterator
#
# LeetCode: 341
# Difficulty: Medium
# Pattern: Iterator design
#
# Problem:
# You are given a nested list of integers nestedList. Each element is either an integer or
# a list whose elements may also be integers or other lists. Implement an iterator to flatten it.
#
# Implement the NestedIterator class:
# - NestedIterator(List<NestedInteger> nestedList) Initializes the iterator with the nested
#   list nestedList.
# - int next() Returns the next integer in the nested list.
# - boolean hasNext() Returns True if there are still some integers in the nested list and
#   False otherwise.
#
# Example 1:
# Input: nestedList = [[1, 1], 2, [1, 1]]
# Output: [1, 1, 2, 1, 1]
#
# Example 2:
# Input: nestedList = [1, [4, [6]]]
# Output: [1, 4, 6]
#
# Constraints:
# - 1 <= nestedList.length <= 500
# - The values of the integers in the nested list is in the range [-10^6, 10^6]

# NestedInteger is provided by the judge. For local practice, use nested Python lists.
class NestedIterator:
    def __init__(self, nested_list):
        pass

    def next(self):
        pass

    def has_next(self):
        pass


if __name__ == '__main__':
    nested_list = [[1, 1], 2, [1, 1]]
    it = NestedIterator(nested_list)
    result = []
    while it.has_next():
        result.append(it.next())
    print(result)
