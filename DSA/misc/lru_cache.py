from collections import deque



class LRUCache:

    def __init__(self, capacity: int):
        self.cache = {}
        # self.limit is unnecessary and error-prone; remove its usage.
        # self.limit = 0  # <-- REMOVE THIS LINE
        self.capacity = capacity
        self.dqueue = deque()

    def remove_key(self, key):
        # Add exception handling so no ValueError is raised if key not found in deque.
        try:
            self.dqueue.remove(key)
        except ValueError:
            pass  # Key may already not be present in deque

    def remove_last(self):
        val = self.dqueue.pop()
        self.cache.pop(val)
        # No further changes needed here

    def add_key_at_start(self, key):
        self.dqueue.appendleft(key)

    def get(self, key: int) -> int:
        if key in self.cache:
            # remove the key from dqueue
            self.remove_key(key)
            # add it to the start of the dqueue 
            self.add_key_at_start(key)
            return self.cache.get(key)
        # Return -1 for not found, which is standard LRU practice
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache[key] = value
            # update the dqueue
            self.remove_key(key)
            self.add_key_at_start(key)
            return
        # Use len(self.cache) for capacity instead of self.limit
        elif key not in self.cache and len(self.cache) == self.capacity:
            # remove the key from dqueue and from cache
            self.remove_last()
        self.cache[key] = value
        self.add_key_at_start(key)
        # No need to manually increment a limit/counter
        return



def test_LRUCache():
    # Example usage:
    lru = LRUCache(2)     # capacity = 2

    # Try put
    print("Put (1, 10)")
    lru.put(1, 10)
    print("Put (2, 20)")
    lru.put(2, 20)

    # Get something
    print("Get 1:", lru.get(1))    # Should print cached value for key 1, if implemented

    print("Put (3, 30)")
    lru.put(3, 30)   # This should evict the least recently used key

    print("Get 2:", lru.get(2))    # May print -1 or None or not found if 2 evicted

    print("Put (4, 40)")
    lru.put(4, 40)

    print("Get 1:", lru.get(1))    # Should print -1 or None if 1 was evicted
    print("Get 3:", lru.get(3))    # Should print 30 if present
    print("Get 4:", lru.get(4))    # Should print 40 if present

if __name__ == "__main__":
    test_LRUCache()


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)