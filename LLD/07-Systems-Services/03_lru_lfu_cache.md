# LRU / LFU Cache

> O(1) cache with eviction policy → **hashmap + linked list; Strategy for policy**. 🟡

## Scope / Requirements

**In scope**
- Capacity `N`; `get` / `put` in average O(1) for LRU.
- Evict least recently used (LRU) or least frequently used (LFU) when full.
- Update recency/frequency on get and put.

**Out of scope**
- Distributed cache, TTL (can mention), persistence.

**Domain invariants**
- Size ≤ capacity always.
- LRU: most recently accessed at head (or tail — pick one); victim is opposite end.
- LFU: evict minimum frequency; tie-break with LRU among same frequency (classic).
- `get` miss does not insert; `put` updates value in place and refreshes metadata.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Node` | key, value, links / freq. |
| `LRUCache` | map + doubly linked list. |
| `LFUCache` | map + freq lists. |
| `Cache` interface | Unified `get`/`put` for Strategy demos. |

## Key Interfaces / Patterns

- **HashMap + Doubly Linked List** for LRU O(1).
- **Strategy** if interviewer wants pluggable policy behind one cache API.
- LFU: map key→node, map freq→DLL, track minFreq.

## End-to-End Flow (LRU)

1. `put(1,"a")` … fill to capacity.
2. `get(1)` moves key 1 to MRU position.
3. `put(new)` evicts LRU key, inserts new as MRU.

## Python Skeleton

```python
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Node:
    key: Any
    value: Any
    prev: Optional["Node"] = None
    next: Optional["Node"] = None


class DoublyLinkedList:
    def __init__(self):
        self.head = Node(None, None)  # dummy
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_to_front(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None

    def pop_lru(self) -> Node:
        node = self.tail.prev
        self.remove(node)
        return node


class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: dict[Any, Node] = {}
        self.list = DoublyLinkedList()

    def get(self, key: Any) -> Any | None:
        node = self.map.get(key)
        if not node:
            return None
        self.list.remove(node)
        self.list.add_to_front(node)
        return node.value

    def put(self, key: Any, value: Any) -> None:
        if key in self.map:
            node = self.map[key]
            node.value = value
            self.list.remove(node)
            self.list.add_to_front(node)
            return
        if len(self.map) >= self.cap:
            lru = self.list.pop_lru()
            del self.map[lru.key]
        node = Node(key, value)
        self.map[key] = node
        self.list.add_to_front(node)


class LFUCache:
    """Concise LFU: freq map + min_freq. Lists are deques of keys for brevity."""

    def __init__(self, capacity: int):
        from collections import defaultdict, OrderedDict
        self.cap = capacity
        self.val: dict[Any, Any] = {}
        self.freq: dict[Any, int] = {}
        self.groups: dict[int, OrderedDict] = defaultdict(OrderedDict)
        self.minf = 0

    def _touch(self, key: Any) -> None:
        f = self.freq[key]
        del self.groups[f][key]
        if f == self.minf and not self.groups[f]:
            self.minf += 1
        self.freq[key] = f + 1
        self.groups[f + 1][key] = None

    def get(self, key: Any) -> Any | None:
        if key not in self.val:
            return None
        self._touch(key)
        return self.val[key]

    def put(self, key: Any, value: Any) -> None:
        if self.cap <= 0:
            return
        if key in self.val:
            self.val[key] = value
            self._touch(key)
            return
        if len(self.val) >= self.cap:
            evict, _ = self.groups[self.minf].popitem(last=False)
            del self.val[evict]
            del self.freq[evict]
        self.val[key] = value
        self.freq[key] = 1
        self.groups[1][key] = None
        self.minf = 1
```

## Go Skeleton

```go
package cache

type node struct {
    key, value any
    prev, next *node
}

type LRUCache struct {
    cap        int
    table      map[any]*node
    head, tail *node // dummies
}

func NewLRU(capacity int) *LRUCache {
    h, t := &node{}, &node{}
    h.next, t.prev = t, h
    return &LRUCache{cap: capacity, table: map[any]*node{}, head: h, tail: t}
}

func (c *LRUCache) addFront(n *node) {
    n.next = c.head.next
    n.prev = c.head
    c.head.next.prev = n
    c.head.next = n
}

func (c *LRUCache) remove(n *node) {
    n.prev.next = n.next
    n.next.prev = n.prev
}

func (c *LRUCache) Get(key any) (any, bool) {
    n, ok := c.table[key]
    if !ok {
        return nil, false
    }
    c.remove(n)
    c.addFront(n)
    return n.value, true
}

func (c *LRUCache) Put(key, value any) {
    if n, ok := c.table[key]; ok {
        n.value = value
        c.remove(n)
        c.addFront(n)
        return
    }
    if len(c.table) >= c.cap {
        lru := c.tail.prev
        c.remove(lru)
        delete(c.table, lru.key)
    }
    n := &node{key: key, value: value}
    c.table[key] = n
    c.addFront(n)
}
```

## Concurrency / Consistency

- Single mutex around get/put for interview.
- Concurrent LRU is hard (striping / approx LRU like CLOCK) — mention as trade-off.
- Read-heavy: segmented LRU / concurrent maps with weaker recency.

## Extensions / Trade-offs / Pitfalls

- TTL + LRU; size in bytes vs entry count.
- Pitfall: forgetting move-to-front on `put` update.
- Pitfall: LFU minFreq not updated when freq list empties.
- Weak vs strong consistency in distributed cache — different problem.

## Interview Discussion Points

- Why DLL + map, not list.scan?
- LRU vs LFU workloads (scan resistance)?
- How does Redis approximate LRU?

## Exercise

Implement LRU capacity 2; sequence put/get that proves eviction order.

**Follow-ups**
1. Implement LFU with OrderedDict freq buckets.
2. Add thread safety with one mutex; discuss bottlenecks.
3. Design a `CachePolicy` interface and swap LRU/LFU.
