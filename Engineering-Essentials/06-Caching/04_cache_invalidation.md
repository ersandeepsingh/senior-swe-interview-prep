# Cache Invalidation

> “There are only two hard things in Computer Science: cache invalidation and naming things.” Invalidation is how you keep the cache **honest** after the source of truth changes — balancing **staleness** vs **freshness**.

## Plain English

When data changes in the DB, the cache may still hold the old value. You must either:

1. **Delete (invalidate)** the key so the next read refills.  
2. **Update** the key with the new value.  
3. **Expire** via TTL and accept temporary staleness.  
4. **Version** keys (`product:42:v7`) so old entries become unreachable.

```text
  Write path (common):
    UPDATE DB ──success──► DEL cache:key
                              │
                         next GET misses → refill from DB

  Stale window if you skip invalidate:
    DB = new   Cache = old   ← readers see lie
```

## Essentials (must-know for this topic)

### Invalidation approaches compared

| Approach | How it works | Freshness | Cost / risk |
|----------|--------------|-----------|-------------|
| **Delete on write** | After DB OK → `DEL` key | Fast | Must know every dependent key |
| **Update on write** | Write new value into cache | Warm hit path | Stale-overwrite races |
| **TTL-only** | Let entry age out | Bounded staleness | Origin load; sync expiry |
| **Versioned keys** | `product:42:vN` / generation bump | Instant “logical” invalidate | Old keys linger until TTL/evict |
| **Event / CDC invalidate** | Stream of changes → delete keys | Decoupled writers | Lag; at-least-once dup deletes |

### Key terms

| Term | Meaning |
|------|---------|
| **Stale** | Cache value ≠ source of truth |
| **Fan-out** | One write touches many cached views (home, category, …) |
| **Stampede after invalidate** | Popular key deleted → many simultaneous refills |
| **Write-then-delete race** | Slow reader refills cache with pre-write DB snapshot |

**Safe default order:** commit DB → delete cache → TTL as backstop. Prefer delete over update unless you version/CAS.

## Simple example

**Price change on SKU 100:**

```text
  Bad:  UPDATE prices SET amount=99 WHERE sku=100
        (forget cache) → homepage still shows ₹149 for minutes

  Better:
        UPDATE prices ...
        DEL product:100
        (optional) DEL product:100:related, category:shoes:page:1
```

**Fan-out problem:** one product change may touch many cached pages (home, category, search snippets). Either invalidate a **known key set**, use **short TTL** on aggregates, or **version** the catalog.

## When to use / trade-offs

| Prefer **delete on write** when… | Prefer **TTL-only** when… |
|----------------------------------|---------------------------|
| You know the keys; freshness matters | Aggregates are hard to enumerate |
| Strong read-your-writes expectation | Brief staleness is OK |

| Prefer **update on write** when… | Prefer **versioned keys** when… |
|----------------------------------|----------------------------------|
| Hot keys must stay warm | Deployments / schema shifts; bulk invalidation |
| Single key maps cleanly to entity | You can bump a generation id |

| Approach | You gain | You give up |
|----------|----------|-------------|
| Explicit invalidate | Fast freshness | Must know every dependent key |
| Short TTL | Simple | More origin load; sync expiry risk |
| Event-driven invalidate (CDC) | Decoupled writers | Pipeline lag; at-least-once dup deletes |
| Write-through update | Warm cache | Dual-write failure modes |

## Pitfalls

- **Partial invalidation** — update product, forget category page cache.  
- **Race:** invalidate, then a slow reader writes **old** DB snapshot back into cache (use version/CAS or “write DB then delete,” and short TTL as backstop).  
- Invalidating too broadly → stampede on origin.  
- “We’ll invalidate everything” with `FLUSHALL` in prod.

## Interview trigger phrase

> “I’d **write the DB first, then delete the cache key**, keep a **TTL as a safety net**, and for fan-out pages either short TTL or an explicit dependent-key list — never rely on hope.”

## Exercise

**Design invalidation for a blog.**

1. Author edits a post — which keys die (post, author page, home feed, sitemap)?  
2. Home feed is “latest 20 posts” — invalidate vs short TTL vs version?  
3. Two writers edit the same post; one stale refill races — how do you stop the old value winning?
