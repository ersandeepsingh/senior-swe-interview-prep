# Blob / Object Storage

> **Object stores** (S3-style) hold large opaque bytes — images, videos, backups, dumps — addressed by key, not by row. Cheap, durable, scalable; **not** your transactional database.

## Plain English

| | Object / blob store | Block / DB / FS |
|---|---------------------|-----------------|
| Unit | Object (key → bytes + metadata) | Blocks, rows, files with POSIX |
| Access | HTTP GET/PUT, presigned URLs | Mount, SQL, local path |
| Strength | Durability at scale, cost for large media | Low-latency small updates |

```text
  Client                     App / CDN
    │                          │
    │ 1. auth request          │
    ▼                          ▼
  API ──► issue presigned URL ──► Client PUT/GET directly to object store
                                  (app never proxies 2GB video)

  ┌─────────────────────────────────────┐
  │  bucket: media-prod                 │
  │  key: users/42/avatar/v3.jpg        │
  │  metadata: content-type, cache-ctl  │
  └─────────────────────────────────────┘
         ▲
         │ references only (URL / key) in Postgres
```

## Simple example

**Photo-sharing app.**

| What lives where | Why |
|------------------|-----|
| Photo bytes in S3 / GCS / Azure Blob | Cheap GB-month; 11-nines class durability stories |
| `photo_id`, `owner_id`, `s3_key`, captions in SQL | Queryable metadata + ACID ownership |
| CDN in front of bucket | Edge latency for reads |

```text
  Upload:
    App inserts row (status=pending) → presigned PUT → client uploads
    → webhook/complete → status=ready → CDN URL to clients

  Never:
    store 20MB images as BYTEA in Postgres 💥
```

**Also common:** DB snapshots, log archives, ML datasets, static site assets.

## Why prefer one over the other

| Prefer **object storage** when… | Prefer **DB / disk on app** when… |
|---------------------------------|-----------------------------------|
| Large immutable-ish blobs | Tiny fields queried/filtered often |
| Need durability + lifecycle tiers (hot/cold) | Sub-ms random small reads/writes |
| Clients can upload/download directly | Transactional update of structure |

**Why not replace the database with S3?** No rich query, weak cross-object transactions, listing is not a query engine.

**Why lifecycle policies?** Move old backups to Glacier/Archive classes — cost control interviewers love.

### Real systems (interview name-drops)

- **AWS S3**, **GCS**, **Azure Blob**, MinIO (self-hosted).
- **CDN:** CloudFront, Fastly, Cloudflare in front of buckets.
- **Presigned URLs** for secure direct upload without making the bucket public.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Blobs in object store | Cost, scale, durability | Extra system; eventual consistency edge cases on listing |
| Presigned direct upload | App servers stay thin | Need careful expiry, virus scan, content-type checks |
| CDN caching | Global read latency | Cache invalidation on replace |
| Store URLs only in DB | Clean separation | Broken links if keys deleted without GC |

**Common interview trap:** Putting media through the app tier as a streaming proxy “for security.” Seniors use **presigned URLs** + private buckets + CDN.

## Interview trigger phrase

> “I’d keep **bytes in object storage**, **metadata in the DB**, and use **presigned URLs + CDN** so the API never ships multi-MB payloads.”

## Exercise

**Design media storage for a chat app (images + short video).**

1. What is stored in S3 vs Postgres for a message with an attachment?  
2. User deletes a chat — how do you garbage-collect orphaned objects without racing new uploads?  
3. One sentence on hot vs cold storage classes for attachments older than 90 days.
