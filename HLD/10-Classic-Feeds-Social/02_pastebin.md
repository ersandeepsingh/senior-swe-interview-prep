# Design a Pastebin 🟡

> **Crux:** Separate large blob content from metadata, store blobs in object storage, and enforce TTL/expiry cleanly.

## Clarify (say this first)

**Functional**
- Create paste (text/code) → unique URL; fetch by ID; optional syntax highlight client-side
- Optional password, burn-after-read, custom expiry (1h / 1d / never)
- List “my pastes” if authenticated; anonymous create allowed
- Soft size cap (e.g. 1 MB text) unless interviewer expands to files

**Non-functional**
- Read-heavy after create; create latency OK if async upload
- Availability over strong consistency on reads of old pastes
- Cheap storage for cold/expired data; durable until TTL
- Abuse: rate limits, size limits, malware scanning optional

## Back-of-envelope

```text
Assumptions: 10M pastes/day, avg 10 KB body ≈ 100 GB/day raw
Metadata ~200 B/paste → negligible vs blob
Read:write ~20:1 → peak create ~200/s, read ~4K/s
Hot pastes: cache metadata + small bodies; large → object store + CDN
TTL: most expire in 24h → lifecycle rules reclaim space
```

## API + data model

```text
POST   /api/v1/pastes           { content, ttl?, password?, visibility }
GET    /api/v1/pastes/:id       → content + meta (or redirect to signed URL)
DELETE /api/v1/pastes/:id       → owner delete / burn-after-read
GET    /api/v1/users/:id/pastes → list metadata only
```

| Entity | Fields |
|--------|--------|
| `paste_meta` | `paste_id`, `owner_id?`, `title?`, `size`, `content_type`, `blob_key`, `expires_at`, `burn`, `created_at` |
| Object store | `blob_key` → raw bytes (S3/GCS) |
| `paste_access` (optional) | password hash, view count |

## High-level architecture

```text
Client → LB → Paste API
                │
                ├─► write meta (SQL/KV) + put object (S3)
                │
                └─► on GET: meta cache → signed URL / stream blob
                                    │
                         Object storage + CDN (optional)
                         TTL sweeper / S3 lifecycle
```

## Deep dive: the crux

**Why not put the whole paste in SQL?** Large text bloats rows, backups, and replication. Pattern: **metadata in DB, body in object storage**.

| Approach | Pros | Cons | Pick when |
|----------|------|------|-----------|
| Body in DB (TEXT) | Simple txs | Poor at size/scale | Tiny pastes, low volume |
| Body in object store | Cheap, scalable, lifecycle | Two writes; consistency of meta↔blob | Default interview answer |
| Inline small / object large | Fast hot path for snippets | Dual path complexity | Mixed size distribution |

**Expiry**
- Store `expires_at` on meta; S3 lifecycle or sweeper deletes blob
- Cache with TTL ≤ remaining life; burn-after-read = delete meta+blob after first successful GET
- Never rely on cache alone for security (password / burn)

**Create atomicity:** write blob first, then meta (orphan GC job); or meta `pending` → upload → `active`. Prefer idempotent `paste_id` from client or server.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Object store for body | Cost + scale | Extra hop; eventual GC of orphans |
| Signed URLs | Offload bandwidth from API | Short-lived URL UX; harder password gate |
| Aggressive CDN | Fast public reads | Harder private/password pastes |
| Sync delete on burn | Correctness | Higher GET latency / lock |

## Failure modes & scale

- **Orphan blobs:** upload succeeded, meta failed — periodic GC by prefix/age
- **Sweeper lag:** serve 404 when `expires_at < now` even if blob still exists
- **Hot paste:** cache meta + body under size threshold; else CDN
- **Password pastes:** never put body on CDN; check auth then stream
- **Shard meta** by `paste_id`; object store scales independently

## Interview trigger phrase

> “I’d keep paste metadata in a DB with `expires_at`, put the body in object storage keyed by paste ID, and use lifecycle rules plus a sweeper for TTL — the API never treats the blob store as the source of truth for expiry.”

## Exercise

1. Design **burn-after-read** under concurrent GETs (two tabs) without double-serving.
2. How do you handle a **1 GB file paste** differently from a 10 KB snippet?
3. What consistency do you promise between “list my pastes” and a just-created paste?
