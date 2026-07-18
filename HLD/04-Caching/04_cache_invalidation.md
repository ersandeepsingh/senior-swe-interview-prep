# Cache Invalidation

> **Invalidation** keeps the cache from serving lies after the source of truth changes. It’s the hard part: **delete**, **update**, or **version** the key — and race-safe under concurrency.

## Plain English

| Approach | Idea | Typical use |
|----------|------|-------------|
| **TTL expiry** | Don’t explicitly invalidate; age out | Low risk of stale; eventual OK |
| **Delete on write** | Writer updates DB, then `DEL` cache key | Cache-aside default |
| **Update on write** | Writer sets new value in cache | Keep hot keys warm |
| **Versioned keys** | `product:42:v7` — bump version on change | Avoid stale overwrite races |
| **Pub/sub invalidate** | Write broadcasts “evict key” to nodes | Local caches across pods |
| **Purge CDN** | Explicit edge invalidation | Same-URL static/media |

Famous line still true: invalidation is easy to *say*, hard to get **race-free**.

```text
  Writer                         Readers
    │                               │
    ▼                               ▼
  UPDATE DB                    GET cache (miss)
    │                               │
    ▼                               ▼
  DEL cache key                SELECT DB (old??)
    │                               │
    │                               ▼
    │                          SET cache ← stale 💥
    ▼
  (need versioning / locking / short TTL)
```

## Simple example

**Inventory count for a flash sale SKU:**

```text
  Bad:  write DB → update cache value (races with concurrent writers)
  OK:   write DB → DEL inventory:{sku} → next reader reloads
  Better for races:
        write DB with version++ → cache key includes version
        or use compare-and-set / Lua so stale SET can’t win
```

Catalog description: TTL 5 minutes may be enough — invalidation optional. Inventory: **must** invalidate (or skip caching writes path) or you oversell.

## Why prefer one over the other

| Prefer **DEL on write** when… | Prefer **TTL-only** when… |
|-------------------------------|---------------------------|
| Stale is user-visible / costly | Slightly stale OK (feeds, rankings) |
| Keyspace known and small | Invalidation fan-out is painful |

| Prefer **versioned keys** when… | Prefer **pub/sub flush** when… |
|---------------------------------|--------------------------------|
| Concurrent read refill races hurt | Many local in-process caches |
| You already version domain objects | Redis shared cache already coherent enough |

**Not “update cache in place is always faster.”** It’s a footgun under concurrent writers unless you have ordering/version checks.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| DEL on write | Simple; avoids writing stale | Extra miss after every write |
| Update on write | Warm cache | Stale SET races |
| Short TTL | Safety net | More DB load |
| Synchronous multi-layer purge | Fresher global view | Latency; partial purge failures |
| Eventual invalidation bus | Decoupled services | Delivery delay → stale window |

## Interview trigger phrase

> “On write I’d **update the database then delete the cache key**, with **TTL as a safety net** — and for hot contested keys I’d use **versioned values** so a slow reader can’t SET stale data back.”

## Exercise

**Invalidate caches for a blogging platform.**

1. Author edits a post — CDN HTML, Redis `post:{id}`, and local app cache: order of operations?  
2. Two editors save at once — describe a stale SET race and how versioning fixes it.  
3. Invalidation topic loses messages for 30s — what’s your safety net so users don’t see forever-stale posts?
