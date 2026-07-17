# In-Memory Key-Value Store

> get/put with TTL & eviction → **composition + eviction policy**. 🟡

## Scope / Requirements

**In scope**
- `put(key, value)`, `get(key)`, `delete(key)`.
- Optional TTL; expire lazily on access and/or via sweeper.
- Capacity limit with eviction policy (LRU hook).

**Out of scope**
- Disk WAL, replication, Redis cluster protocol.

**Domain invariants**
- `get` never returns expired entries (treat as miss + delete).
- At most one value per key; put overwrites and refreshes TTL if provided.
- If capacity set, size ≤ capacity after put (evict before/after insert).
- TTL expiry time is absolute (`now + ttl`), not renewed on get unless “sliding TTL” is specified.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Store` | Public API. |
| `Entry` | Value + expireAt. |
| `EvictionPolicy` | Choose victim key. |
| `Clock` | Testable time. |

## Key Interfaces / Patterns

- **Composition:** map + policy + clock.
- **Strategy — eviction:** LRU/LFU/random.
- Separate TTL concerns from eviction (both can remove keys).

## End-to-End Flow

1. `put("a", 1, ttl=5s)` stores entry with expireAt.
2. `get("a")` before expiry returns 1 and records access for LRU.
3. After expiry or capacity pressure, entry gone.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import time


@dataclass
class Entry:
    value: Any
    expire_at: Optional[float]  # monotonic seconds; None = forever


class EvictionPolicy(ABC):
    @abstractmethod
    def record_get(self, key: str) -> None: ...
    @abstractmethod
    def record_put(self, key: str) -> None: ...
    @abstractmethod
    def record_remove(self, key: str) -> None: ...
    @abstractmethod
    def victim(self) -> Optional[str]: ...


class LRUPolicy(EvictionPolicy):
    def __init__(self):
        self._order: list[str] = []  # sketch; use OrderedDict in real code

    def record_get(self, key: str) -> None:
        if key in self._order:
            self._order.remove(key)
            self._order.append(key)

    def record_put(self, key: str) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def record_remove(self, key: str) -> None:
        if key in self._order:
            self._order.remove(key)

    def victim(self) -> Optional[str]:
        return self._order[0] if self._order else None


class KVStore:
    def __init__(self, capacity: Optional[int] = None, policy: Optional[EvictionPolicy] = None):
        self._data: dict[str, Entry] = {}
        self.capacity = capacity
        self.policy = policy or LRUPolicy()

    def _now(self) -> float:
        return time.monotonic()

    def _expired(self, e: Entry) -> bool:
        return e.expire_at is not None and e.expire_at <= self._now()

    def _purge_if_expired(self, key: str) -> None:
        e = self._data.get(key)
        if e and self._expired(e):
            del self._data[key]
            self.policy.record_remove(key)

    def get(self, key: str) -> Any | None:
        self._purge_if_expired(key)
        e = self._data.get(key)
        if not e:
            return None
        self.policy.record_get(key)
        return e.value

    def put(self, key: str, value: Any, ttl_sec: float | None = None) -> None:
        expire = self._now() + ttl_sec if ttl_sec is not None else None
        if key not in self._data and self.capacity is not None and len(self._data) >= self.capacity:
            v = self.policy.victim()
            if v is not None:
                del self._data[v]
                self.policy.record_remove(v)
        self._data[key] = Entry(value, expire)
        self.policy.record_put(key)

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self.policy.record_remove(key)
```

## Go Skeleton

```go
package kv

import (
    "sync"
    "time"
)

type Entry struct {
    Value    any
    ExpireAt time.Time // zero => no TTL
}

type EvictionPolicy interface {
    RecordGet(key string)
    RecordPut(key string)
    RecordRemove(key string)
    Victim() (string, bool)
}

type Store struct {
    mu       sync.RWMutex
    data     map[string]Entry
    capacity int // 0 = unbounded
    policy   EvictionPolicy
}

func New(capacity int, policy EvictionPolicy) *Store {
    return &Store{data: map[string]Entry{}, capacity: capacity, policy: policy}
}

func (s *Store) expired(e Entry, now time.Time) bool {
    return !e.ExpireAt.IsZero() && !e.ExpireAt.After(now)
}

func (s *Store) Get(key string) (any, bool) {
    s.mu.Lock()
    defer s.mu.Unlock()
    e, ok := s.data[key]
    if !ok {
        return nil, false
    }
    if s.expired(e, time.Now()) {
        delete(s.data, key)
        s.policy.RecordRemove(key)
        return nil, false
    }
    s.policy.RecordGet(key)
    return e.Value, true
}

func (s *Store) Put(key string, value any, ttl time.Duration) {
    s.mu.Lock()
    defer s.mu.Unlock()
    if _, exists := s.data[key]; !exists && s.capacity > 0 && len(s.data) >= s.capacity {
        if v, ok := s.policy.Victim(); ok {
            delete(s.data, v)
            s.policy.RecordRemove(v)
        }
    }
    e := Entry{Value: value}
    if ttl > 0 {
        e.ExpireAt = time.Now().Add(ttl)
    }
    s.data[key] = e
    s.policy.RecordPut(key)
}
```

## Concurrency / Consistency

- `RWMutex`: many gets, exclusive puts; or shard by key hash.
- Eviction + put must be one critical section to avoid exceeding capacity.
- Lazy TTL vs background sweeper — sweeper needs same locks.

## Extensions / Trade-offs / Pitfalls

- Sliding TTL on get; CAS / compare-and-set ops.
- Pitfall: forgetting to update eviction structure on overwrite.
- Persistence: snapshot + AOF as interview extension narrative.

## Interview Discussion Points

- Lazy expiry vs active expiry — memory vs CPU?
- How is this different from “just a cache”? (primary store vs cache semantics)
- What happens on `put` when capacity=1 and key already exists?

## Exercise

Implement get/put/delete with TTL and capacity-1 store using LRU victim.

**Follow-ups**
1. Add `TTL(key) -> remaining`.
2. Make get concurrent-safe with RWMutex narrative in Go.
3. When would you prefer LFU eviction over LRU?
