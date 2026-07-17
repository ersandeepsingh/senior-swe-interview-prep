# URL Shortener (LLD)

> Encode/decode, collision handling → **Strategy (encoding) + repository**. 🟡

## Scope / Requirements

**In scope**
- `shorten(long_url) -> short_code`; `resolve(short_code) -> long_url`.
- Custom alias optional; default code from counter or hash.
- Persist mapping; handle collisions.

**Out of scope**
- Full analytics product, CDN edge design (mention), multi-region active-active deep dive.

**Domain invariants**
- `short_code` uniquely maps to one long URL (or versioned — keep 1:1 for interview).
- Resolve of unknown code → not found.
- Idempotent shorten of same URL may return existing code (policy — **state it**).
- Codes use allowed alphabet only; length sufficient for expected cardinality.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `URLMapping` | code, long URL, createdAt, optional expiry. |
| `URLRepository` | save, findByCode, findByLong. |
| `Encoder` / `IDGenerator` | Strategy: base62(counter) vs hash. |
| `URLService` | Orchestrate shorten/resolve. |

## Key Interfaces / Patterns

- **Strategy — encoding / id generation.**
- **Repository** for persistence port.
- **Facade** service API.

## End-to-End Flow

1. User submits long URL → service allocates id → base62 encode → store → return `https://short/xY9`.
2. Redirect hit → lookup code → 302 to long URL (or 404).

## Python Skeleton

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    out = []
    while num:
        num, rem = divmod(num, 62)
        out.append(ALPHABET[rem])
    return "".join(reversed(out))


@dataclass
class URLMapping:
    code: str
    long_url: str


class URLRepository(ABC):
    @abstractmethod
    def save(self, m: URLMapping) -> None: ...
    @abstractmethod
    def find_by_code(self, code: str) -> Optional[URLMapping]: ...
    @abstractmethod
    def find_by_long(self, long_url: str) -> Optional[URLMapping]: ...


class InMemoryURLRepo(URLRepository):
    def __init__(self):
        self.by_code: dict[str, URLMapping] = {}
        self.by_long: dict[str, URLMapping] = {}

    def save(self, m: URLMapping) -> None:
        self.by_code[m.code] = m
        self.by_long[m.long_url] = m

    def find_by_code(self, code: str) -> Optional[URLMapping]:
        return self.by_code.get(code)

    def find_by_long(self, long_url: str) -> Optional[URLMapping]:
        return self.by_long.get(long_url)


class CodeGenerator(ABC):
    @abstractmethod
    def next_code(self) -> str: ...


class CounterBase62(CodeGenerator):
    def __init__(self, start: int = 1):
        self._n = start

    def next_code(self) -> str:
        code = base62_encode(self._n)
        self._n += 1
        return code


class URLService:
    def __init__(self, repo: URLRepository, gen: CodeGenerator):
        self.repo = repo
        self.gen = gen

    def shorten(self, long_url: str, alias: str | None = None) -> str:
        existing = self.repo.find_by_long(long_url)
        if existing and alias is None:
            return existing.code
        code = alias or self.gen.next_code()
        if self.repo.find_by_code(code):
            if alias:
                raise RuntimeError("alias taken")
            # collision on generator — retry
            return self.shorten(long_url)
        self.repo.save(URLMapping(code, long_url))
        return code

    def resolve(self, code: str) -> str:
        m = self.repo.find_by_code(code)
        if not m:
            raise KeyError("not found")
        return m.long_url
```

## Go Skeleton

```go
package shortener

import (
    "errors"
    "sync"
)

const alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

func Base62Encode(n int64) string {
    if n == 0 {
        return string(alphabet[0])
    }
    var b []byte
    for n > 0 {
        b = append([]byte{alphabet[n%62]}, b...)
        n /= 62
    }
    return string(b)
}

type Mapping struct {
    Code, LongURL string
}

type Repository interface {
    Save(Mapping) error
    FindByCode(code string) (Mapping, bool)
    FindByLong(url string) (Mapping, bool)
}

type MemoryRepo struct {
    mu     sync.RWMutex
    byCode map[string]Mapping
    byLong map[string]Mapping
}

func NewMemoryRepo() *MemoryRepo {
    return &MemoryRepo{byCode: map[string]Mapping{}, byLong: map[string]Mapping{}}
}

func (r *MemoryRepo) Save(m Mapping) error {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.byCode[m.Code] = m
    r.byLong[m.LongURL] = m
    return nil
}

func (r *MemoryRepo) FindByCode(code string) (Mapping, bool) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    m, ok := r.byCode[code]
    return m, ok
}

func (r *MemoryRepo) FindByLong(url string) (Mapping, bool) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    m, ok := r.byLong[url]
    return m, ok
}

type CounterGen struct {
    mu sync.Mutex
    n  int64
}

func (c *CounterGen) Next() string {
    c.mu.Lock()
    defer c.mu.Unlock()
    code := Base62Encode(c.n)
    c.n++
    return code
}

type Service struct {
    Repo Repository
    Gen  *CounterGen
}

func (s *Service) Shorten(longURL, alias string) (string, error) {
    if alias == "" {
        if m, ok := s.Repo.FindByLong(longURL); ok {
            return m.Code, nil
        }
    }
    code := alias
    if code == "" {
        code = s.Gen.Next()
    }
    if _, taken := s.Repo.FindByCode(code); taken {
        return "", errors.New("collision")
    }
    _ = s.Repo.Save(Mapping{Code: code, LongURL: longURL})
    return code, nil
}

func (s *Service) Resolve(code string) (string, error) {
    m, ok := s.Repo.FindByCode(code)
    if !ok {
        return "", errors.New("not found")
    }
    return m.LongURL, nil
}
```

## Concurrency / Consistency

- Counter must be atomic (Redis INCR / DB sequence) across instances.
- Unique constraint on `code`; retry on conflict for hash-based generators.
- Cache resolve path heavily; DB is source of truth.

## Extensions / Trade-offs / Pitfalls

- Hash(long)[:k] → collisions rise; counter+base62 avoids that.
- Expiry, custom domains, click analytics events.
- Pitfall: non-idempotent shorten creating many codes for one URL without policy.
- Range of base62 length vs capacity (62^7 …).

## Interview Discussion Points

- Why base62 not base64 for URLs?
- Counter vs hash vs Snowflake id as code input?
- Read-heavy redirect path — caching layers?

## Exercise

Implement shorten/resolve with in-memory repo and base62 counter.

**Follow-ups**
1. Support custom alias with conflict error.
2. Make shorten idempotent for duplicate long URLs.
3. Estimate code length for 10B URLs.
