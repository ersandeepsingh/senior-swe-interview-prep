# Rate Limiter

> Token bucket / sliding window / fixed window → **Strategy per algorithm**. 🟡

## Scope / Requirements

**In scope**
- API: `allow(key) -> bool` (optionally return retry-after).
- At least one algorithm fully coded; others swappable via Strategy.
- Per-key limits (user id / IP).

**Out of scope**
- Distributed Redis cluster setup, gateway product UI, billing tiers.

**Domain invariants**
- Under steady load, allowed rate ≈ configured rate (algorithm-specific burst rules).
- Decisions are based on timestamps / tokens — monotonic clock preferred.
- Keys are independent; one key’s traffic doesn’t consume another’s budget (unless global limit added).

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `RateLimiter` | Facade: `allow(key)`. |
| `LimiterAlgorithm` | Strategy implementation. |
| `TokenBucket` / `FixedWindow` / `SlidingWindow` | Concrete algorithms. |
| `Clock` | Inject time for tests. |

## Key Interfaces / Patterns

- **Strategy:** swap token bucket vs sliding window without changing callers.
- **DIP:** clock + config injection.
- Distributed: mention sticky store (Redis) — still Strategy locally.

## End-to-End Flow

1. Request arrives with `user_id`.
2. `limiter.allow(user_id)` loads/creates bucket state → refill by elapsed time → consume 1 token or deny.
3. Gateway returns 200 or 429.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import time


class Clock(ABC):
    @abstractmethod
    def now(self) -> float: ...


class SystemClock(Clock):
    def now(self) -> float:
        return time.monotonic()


class LimiterAlgorithm(ABC):
    @abstractmethod
    def allow(self, key: str) -> bool: ...


class TokenBucket(LimiterAlgorithm):
    def __init__(self, capacity: float, refill_per_sec: float, clock: Clock):
        self.capacity = capacity
        self.refill = refill_per_sec
        self.clock = clock
        self.tokens: dict[str, float] = defaultdict(lambda: capacity)
        self.updated: dict[str, float] = {}

    def allow(self, key: str) -> bool:
        now = self.clock.now()
        last = self.updated.get(key, now)
        elapsed = now - last
        self.tokens[key] = min(self.capacity, self.tokens[key] + elapsed * self.refill)
        self.updated[key] = now
        if self.tokens[key] >= 1:
            self.tokens[key] -= 1
            return True
        return False


class FixedWindow(LimiterAlgorithm):
    def __init__(self, limit: int, window_sec: float, clock: Clock):
        self.limit = limit
        self.window = window_sec
        self.clock = clock
        self.count: dict[tuple[str, int], int] = defaultdict(int)

    def allow(self, key: str) -> bool:
        bucket = int(self.clock.now() // self.window)
        k = (key, bucket)
        if self.count[k] >= self.limit:
            return False
        self.count[k] += 1
        return True


class SlidingWindowLog(LimiterAlgorithm):
    def __init__(self, limit: int, window_sec: float, clock: Clock):
        self.limit = limit
        self.window = window_sec
        self.clock = clock
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = self.clock.now()
        q = self.hits[key]
        while q and now - q[0] >= self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True


class RateLimiter:
    def __init__(self, algo: LimiterAlgorithm):
        self.algo = algo

    def allow(self, key: str) -> bool:
        return self.algo.allow(key)
```

## Go Skeleton

```go
package ratelimit

import (
    "sync"
    "time"
)

type Clock interface{ Now() time.Time }

type SystemClock struct{}

func (SystemClock) Now() time.Time { return time.Now() }

type Algorithm interface {
    Allow(key string) bool
}

type TokenBucket struct {
    mu       sync.Mutex
    capacity float64
    refill   float64 // tokens per second
    clock    Clock
    tokens   map[string]float64
    updated  map[string]time.Time
}

func NewTokenBucket(cap, refill float64, clock Clock) *TokenBucket {
    return &TokenBucket{
        capacity: cap, refill: refill, clock: clock,
        tokens: map[string]float64{}, updated: map[string]time.Time{},
    }
}

func (t *TokenBucket) Allow(key string) bool {
    t.mu.Lock()
    defer t.mu.Unlock()
    now := t.clock.Now()
    tok, ok := t.tokens[key]
    if !ok {
        tok = t.capacity
    }
    if last, ok := t.updated[key]; ok {
        tok += now.Sub(last).Seconds() * t.refill
        if tok > t.capacity {
            tok = t.capacity
        }
    }
    t.updated[key] = now
    if tok < 1 {
        t.tokens[key] = tok
        return false
    }
    t.tokens[key] = tok - 1
    return true
}

type RateLimiter struct{ Algo Algorithm }

func (r RateLimiter) Allow(key string) bool { return r.Algo.Allow(key) }
```

## Concurrency / Consistency

- Per-key mutex or shard map locks; global lock OK for interview scale.
- Distributed: Redis INCR/EXPIRE or Lua for token bucket — atomicity across nodes.
- Clock skew across nodes affects fixed windows — prefer monotonic + centralized store.

## Extensions / Trade-offs / Pitfalls

- Fixed window burst at boundary; sliding window smoother, more memory.
- Token bucket allows controlled burst = capacity.
- Pitfall: using wall clock that jumps; pitfall: float drift — use integers in production.

## Interview Discussion Points

- Which algorithm for API gateway vs login attempts?
- How do you rate-limit in a multi-instance service?
- Exact vs approximate (sliding window counter)?

## Exercise

Implement token bucket: capacity 5, refill 1/sec; simulate bursts.

**Follow-ups**
1. Add fixed window as alternate Strategy.
2. Make `allow` thread-safe for two keys in parallel.
3. Sketch Redis + Lua for distributed token bucket.
