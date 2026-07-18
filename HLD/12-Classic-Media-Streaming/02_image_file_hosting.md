# Design an Image / File Hosting Service 🟡

> **Crux:** Treat binaries as **immutable blobs** in object storage; serve via **CDN/edge**. API owns metadata + auth; never stream large files through app servers long-term.

## Clarify (say this first)

**Functional**
- Upload image/file; get stable public or signed URL
- Optional: resize/crop variants, virus scan, expiry
- Download / embed; delete & ACL (public / private / link)

**Non-functional**
- Upload & download latency dominated by network, not app
- High read:write ratio; edge cache critical for hot assets
- Durability 11 9s–class (object store); availability for metadata
- Cost: storage + egress; avoid app-tier bandwidth tax

## Back-of-envelope

- 100M users, 2 uploads/day × 2 MB → ~400 TB/day ingress (peak lower with concurrency factor)
- Reads 50× writes → CDN must hit >90% or egress kills you
- Metadata: millions of objects → need indexed store; blobs stay in S3-style
- Thumbnails: 3–5 variants × storage — generate async, not on every GET

## API + data model

```text
POST /files                 # returns {file_id, upload_url} (presigned PUT)
PUT  <presigned>            # client → object store direct
POST /files/{id}/complete   # confirm + enqueue processing
GET  /files/{id}            # metadata + CDN/signed URL
DELETE /files/{id}
GET  /files/{id}/variants/{w}x{h}
```

| Entity | Key fields |
|--------|------------|
| File | id, owner, content_type, size, checksum, visibility, status |
| Blob | object_key, bucket, etag |
| Variant | file_id, transform, object_key, cdn_path |
| ACL | file_id, principal, permission |

## High-level architecture

```text
Client ──► API GW ──► Metadata Svc ──► DB (Postgres/Dynamo)
              │              │
              │              └──► Queue ──► Image workers (resize, scan)
              │
              └──► Presigned URL ──► Object Store ◄── CDN Edge ──► Client
```

## Deep dive: the crux

**Blob + edge delivery**
1. Client gets **presigned URL** → PUT straight to object store (app never proxies bytes).
2. On complete: store metadata, enqueue variants.
3. Reads return **CDN URL** (public) or short-lived **signed URL** (private).
4. Cache-Control / immutable keys (`/f/{id}/v/{hash}`) maximize hit rate.

| Alternative | When to pick |
|-------------|--------------|
| Proxy upload through app | Small files only; simpler auth debugging |
| Presigned + object store + CDN | Default at scale |
| Multi-CDN + origin shield | Global + cost/latency sensitive |
| Store blobs in DB | Anti-pattern beyond tiny blobs |

**Private files:** signed cookies/URLs at CDN; or app issues token CDN validates. Don't put secrets in permanent URLs.

**Dedup (optional):** content-hash as object key → save storage; beware shared delete semantics.

**Metadata vs bytes:** DB holds ownership, ACL, content-type, variant map; object store is dumb durable blobs. Never put ACLs only on the CDN URL.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Presigned direct upload | App scales independently | Harder mid-upload progress UX / virus gate timing |
| Immutable content-addressed URLs | Perfect CDN caching | New upload = new URL on edit |
| Eager variant generation | Fast first view | Wasted work on never-viewed sizes |
| Lazy on-demand resize | Save compute | First-hit latency + stampede risk |

## Failure modes & scale

- Incomplete uploads → lifecycle rules / multipart abort; status=PENDING TTL
- Worker lag → serve original until variants ready
- Hot image thundering herd → CDN + coalesce origin requests
- Accidental public leak → default private; audit ACL; short signed TTL
- Scale: shard metadata by file_id/owner; separate hot-path URL service from admin CRUD

## Interview trigger phrase

> “Bytes never transit my app servers — **presigned upload to object storage**, metadata in a DB, **CDN for reads**; variants are async transforms on the blob.”

## Exercise

1. Design private album sharing for 24 hours — URL, auth, and CDN behavior.
2. User replaces an image in-place: how do you invalidate CDN without breaking embeds?
3. Where do you run malware scanning relative to “file is downloadable”?
