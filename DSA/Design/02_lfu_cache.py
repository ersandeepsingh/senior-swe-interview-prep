# LFU Cache
#
# LeetCode: 460
# Difficulty: Hard
# Pattern: LFU cache
#
# Problem:
# Design and implement a data structure for a Least Frequently Used (LFU) cache.
#
# Implement the LFUCache class:
# - LFUCache(int capacity) Initializes the object with the capacity of the data structure.
# - int get(int key) Gets the value of the key if the key exists in the cache. Otherwise,
#   returns -1.
# - void put(int key, int value) Update the value of the key if present, or inserts the key
#   if not already present. When the cache reaches its capacity, it should invalidate and
#   remove the least frequently used key before inserting a new item. For this problem, when
#   there is a tie (i.e., two or more keys with the same frequency), the least recently used
#   key would be invalidated.
#
# The functions get and put must each run in O(1) average time complexity.
#
# Example 1:
# Input:
# ["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"]
# [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]]
# Output: [null, null, null, 1, null, -1, 3, null, -1, 3, 4]
#
# Constraints:
# - 1 <= capacity <= 10^4
# - 0 <= key <= 10^5
# - 0 <= value <= 10^9
# - At most 2 * 10^5 calls will be made to get and put

class LFUCache:
    def __init__(self, capacity):
        pass

    def get(self, key):
        pass

    def put(self, key, value):
        pass


if __name__ == '__main__':
    lfu = LFUCache(2)
    lfu.put(1, 1)
    lfu.put(2, 2)
    print(lfu.get(1))
    lfu.put(3, 3)
    print(lfu.get(2))
    print(lfu.get(3))
    lfu.put(4, 4)
    print(lfu.get(1))
    print(lfu.get(3))
    print(lfu.get(4))
