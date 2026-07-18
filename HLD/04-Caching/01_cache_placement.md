# Cache Placement

> Caching works at **multiple layers** — browser, CDN, app memory, **distributed cache** (Redis), and DB buffer pools. Placement decides **latency, hit rate, and consistency pain**. Seniors say *where* the cache lives before *how* it fills.

## Plain English

| Layer | What’s cached | Shared across users? |
|-------|---------------|----------------------|
| **Client / browser** | JS, CSS, personalized blobs carefully | No (per device) |
| **CDN edge** | Static/media, some public API GETs | Yes (global PoPs) |
| **App local (in-process)** | Hot config, tiny lookups | No (per pod) — fast, inconsistent |
| **Distributed (Redis/Memcached)** | Sessions, product rows, feed fragments | Yes (cluster-wide) |
| **DB / OS page cache** | Recent queries / blocks | Yes (on that DB node) |

Rule of thumb: **closer to user = faster, harder to invalidate globally.**

```text
  Client cache
       │
       ▼
  CDN edge cache
       │
       ▼
  App local memory ──► miss ──► Redis / Memcached
                                   │
                                  miss
                                   │
                                   ▼
                              Database (+ its own buffer cache)
```

## Simple example

**Product detail page** on a marketplace:

```text
  Image CDN          → thumbnail bytes (edge)
  Redis              → product JSON by productId (shared)
  App local Caffeine → “category → top 100 ids” for 30s (per pod OK if slightly stale)
  Postgres           → source of truth on miss / write
  Browser            → hashed bundle app.<hash>.js
```

Price change: invalidate Redis key + purge CDN image if URL reused. Local app cache expires via short TTL — don’t rely on manual fan-out to every pod.

## Why prefer one over the other

| Prefer **CDN** when… | Prefer **Redis** when… | Prefer **local app cache** when… |
|----------------------|------------------------|----------------------------------|
| Same bytes for many users worldwide | Shared mutable-ish app data | Ultra-hot, tiny, TTL-tolerant data |
| Static/media | Sessions, rankings, object graphs | Config flags, feature gates |

| Prefer **only DB cache** when… | Avoid **client cache** when… |
|--------------------------------|------------------------------|
| Hit rate already fine; ops simple | Security-sensitive or must revoke instantly |

**Not “cache everything everywhere.”** Each layer adds invalidation and debugging cost.

## Trade-offs

| Placement | You gain | You give up |
|-----------|----------|-------------|
| Client/CDN | Lowest latency, origin shield | Weak control; purge delays |
| Local in-process | Microsecond reads | Per-pod drift; wasted duplicate memory |
| Distributed Redis | Cross-pod coherence (ish) | Network hop; Redis as critical dep |
| Deeper only (DB) | Simpler mental model | Origin load on every app miss |

## Interview trigger phrase

> “I’d place **static assets on the CDN**, **shared product data in Redis**, and only a **tiny TTL’d local cache** for config — so invalidation stays tractable and pods don’t diverge forever.”

## Exercise

**Design cache layers for a news reader app.**

1. Assign each to a layer: article HTML for anonymous users, per-user “continue reading,” breaking-news banner, MP4 video.  
2. Editor updates a headline — which layers must change, and in what order?  
3. Why is a 5-minute in-process cache dangerous for “user subscription tier”?
