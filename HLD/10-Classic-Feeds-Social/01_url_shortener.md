# Design a URL Shortener (TinyURL) 🟡

> **Crux:** How do you generate unique short keys at high write QPS, and make reads (redirects) cheap via caching?

## Clarify (say this first)

**Functional**
- Shorten a long URL → return a short link; resolve short link → 301/302 redirect
- Optional custom alias; optional expiry / one-time links
- Analytics optional (click counts) — park unless asked
- Assume public + authenticated create; no login required to open

**Non-functional**
- Read-heavy (redirects ≫ creates); p99 redirect under ~50–100 ms
- High availability; short keys unique globally
- Eventual consistency on analytics OK; create must not collide
- Scale: ~100M new URLs/day, 10:1–100:1 read:write

## Back-of-envelope

```text
Assumptions: 100M new URLs/day ≈ 1.2K writes/s (peak ~5–10K)
Read:write 100:1 → ~100K–1M redirects/s peak
Key: base62, 7 chars → 62^7 ≈ 3.5T keys (plenty)
Storage: 100B key + 500B URL + meta ≈ 1KB → 100M/day ≈ 100 GB/day
Hot keys: viral links → cache is mandatory
```

## API + data model

```text
POST   /api/v1/urls          { long_url, custom?, ttl? } → { short_code, short_url }
GET    /:short_code          → 301 Location: long_url
GET    /api/v1/urls/:code    → metadata (owner, created, clicks)
DELETE /api/v1/urls/:code    → soft-delete / expire
```

| Entity | Fields |
|--------|--------|
| `url_mapping` | `short_code` (PK), `long_url`, `user_id?`, `created_at`, `expires_at?`, `status` |
| `click_event` (optional) | `short_code`, `ts`, `geo`, `ua` — append-only / analytics store |

## High-level architecture

```text
Client → CDN/Edge → LB → API (create)
                           │
                           ▼
                    Key Gen Service ──► KV / DB (short→long)
                           │
Client → Edge cache ───────┴──► Cache (Redis) ──► DB on miss
         (redirect hot path)
```

## Deep dive: the crux

**Key generation alternatives**

| Approach | How | Pros | Cons | Pick when |
|----------|-----|------|------|-----------|
| Hash (MD5/SHA) + truncate | Hash long URL → take N chars | No coordination | Collisions; same URL always same key | Dedup by URL matters |
| Counter + base62 | Snowflake / DB sequence → encode | Unique, sortable | Needs ID service; predictable | Default at scale |
| Random | Crypto random in keyspace | Simple | Retry on collision | Low volume |
| Pre-generated pool | Workers fill unused keys | Decouples create latency | Pool ops complexity | Very high create QPS |

**Read path:** cache-aside on `short_code → long_url`; TTL + invalidate on delete/expire. Prefer **302** if you need click logging on every hit; **301** if browser/CDN may cache forever (harder analytics).

**Senior pick:** distributed unique ID (Snowflake-style) → base62; Redis in front of sharded KV/SQL; range/hash shard by `short_code`.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Counter IDs vs hash | Uniqueness without retries | Extra ID service; enumerable keys (mitigate with salt/HMAC) |
| 301 vs 302 | Fewer origin hits (301) | Weaker/click-accurate analytics |
| Cache aggressively | Low redirect latency | Stale after update/delete until TTL |
| Custom aliases | UX | Namespace conflicts, abuse, longer keys |

## Failure modes & scale

- **Hot key / thundering herd:** viral short link — request coalescing, local + Redis cache, CDN
- **ID service down:** pre-allocated ID ranges on app nodes so creates continue
- **DB shard hot:** hash partition keys; avoid sequential counter as shard key
- **Collision on custom alias:** unique constraint + clear 409
- **Abuse:** rate-limit create; malware URL scanning async

## Interview trigger phrase

> “I’d generate keys with a distributed counter encoded in base62, shard a KV store by short code, and put Redis/CDN in front of redirects — the create path owns uniqueness; the read path owns latency.”

## Exercise

1. How would you support **custom aliases** without racing two users for the same name?
2. Walk through **expiry**: who deletes, and how does the cache stay correct?
3. Interviewer says “1B redirects/day on 10 viral keys” — what changes in your design?
