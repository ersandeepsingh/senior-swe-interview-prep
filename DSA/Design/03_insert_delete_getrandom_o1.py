# Insert Delete GetRandom O(1)
#
# LeetCode: 380
# Difficulty: Medium
# Pattern: Randomized set
#
# Problem:
# Implement the RandomizedSet class:
# - RandomizedSet() Initializes the RandomizedSet object.
# - bool insert(int val) Inserts an item val into the set if not present. Returns True if the
#   item was not present, False otherwise.
# - bool remove(int val) Removes an item val from the set if present. Returns True if the
#   item was present, False otherwise.
# - int getRandom() Returns a random element from the current set of elements (it's guaranteed
#   that at least one element exists when this method is called). Each element must have the
#   same probability of being returned.
#
# You must implement the functions of the class such that each function works in average
# O(1) time complexity.
#
# Example 1:
# Input:
# ["RandomizedSet", "insert", "remove", "insert", "getRandom", "remove", "insert", "getRandom"]
# [[], [1], [2], [2], [], [1], [2], []]
# Output: [null, true, false, true, 2, true, false, 2]
#
# Constraints:
# - -2^31 <= val <= 2^31 - 1
# - At most 2 * 10^5 calls will be made to insert, remove, and getRandom
# - There will be at least one element in the data structure when getRandom is called

class RandomizedSet:
    def __init__(self):
        pass

    def insert(self, val):
        pass

    def remove(self, val):
        pass

    def get_random(self):
        pass


if __name__ == '__main__':
    rs = RandomizedSet()
    print(rs.insert(1))
    print(rs.remove(2))
    print(rs.insert(2))
    print(rs.get_random())
    print(rs.remove(1))
    print(rs.insert(2))
    print(rs.get_random())
