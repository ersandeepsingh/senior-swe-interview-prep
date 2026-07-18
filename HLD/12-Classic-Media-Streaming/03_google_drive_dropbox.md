# Design Google Drive / Dropbox 🔴

> **Crux:** **Chunked sync** with **content-defined dedup**, plus **conflict detection** for concurrent/offline edits — not “store a file in S3.”

## Clarify (say this first)

**Functional**
- Upload/download/sync folders across devices; share with ACLs
- Offline edits; version history; selective sync
- Dedup identical content across users (optional product choice)

**Non-functional**
- Sync latency: seconds for small changes; resume large uploads
- Strong enough that users don't lose data; conflicts rare but must be safe
- Bandwidth efficient (delta sync); storage efficient (dedup)
- Multi-device consistency: eventual with clear conflict UX

## Back-of-envelope

- 100M users, avg 10 GB → 1 EB logical; physical << with dedup + compression
- Sync events: bursts when laptop wakes — queue + batch metadata
- Chunk size ~4 MB average (content-defined) → metadata rows explode; need efficient indexes
- Hot path: metadata + small deltas; cold: blob store

## API + data model

```text
POST /namespaces/{id}/changes/watch   # long-poll / websocket cursor
GET  /sync/delta?cursor=              # metadata changes since cursor
POST /files/{id}/commit               # new revision: chunk list + hashes
GET  /chunks/{hash}                   # download chunk (CDN/signed)
PUT  /chunks/{hash}                   # upload if missing (dedup)
```

| Entity | Key fields |
|--------|------------|
| FileNode | id, parent, name, type, head_rev |
| Revision | rev_id, file_id, chunk_hashes[], size, author, ts |
| Chunk | hash, size, refcount, object_key |
| Cursor / Device | device_id, last_cursor, sync_token |
| Lock / Share | resource, ACL, link |

## High-level architecture

```text
Clients (desktop/mobile)
    │  delta / long-poll
    ▼
Sync API ──► Metadata DB (tree, revs, ACLs)
    │
    ├──► Chunk Index (hash → blob)
    │
    └──► Object Store ◄── CDN (chunk GETs)
              ▲
         Dedup: upload only missing hashes
```

## Deep dive: the crux

**1. Chunking**
- Fixed-size: simple; bad for inserts in middle of file.
- **Content-defined chunking (CDC / Rabin):** stable boundaries → better dedup + delta sync. Prefer for Drive-scale.

**2. Dedup**
- Client hashes chunks → server returns which hashes missing → upload only those.
- Cross-user dedup: content-addressed store + refcounts; privacy/legal review.

**3. Sync + conflict**
- Each device has a **cursor** over a change log (or revision vector).
- Concurrent edits on same file → detect via parent_rev mismatch.
- Resolve: last-writer-wins (risky), **keep both** (conflict copy), or OT/CRDT for collab docs (separate product).

| Alternative | When to pick |
|-------------|--------------|
| Whole-file replace | Tiny scale / rare updates |
| Fixed chunks + rsync-ish | Good enough mid-scale |
| CDC + chunk store + conflict copies | Consumer sync at scale (**default**) |
| Full CRDT collab | Google Docs–style co-editing |

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Cross-user dedup | Huge storage save | Complexity, privacy surface |
| Conflict copies | No silent data loss | User clutter |
| Block-level sync | Bandwidth | Chunk metadata overhead |
| Strong per-file locking | Fewer conflicts | Offline UX suffers |

## Failure modes & scale

- Partial commit → transactional metadata: only publish rev when all chunks durable
- Split-brain devices → vector clocks / rev parent checks; never silently merge binary blobs
- Hot shared folder → metadata sharding by namespace; rate-limit change fan-out
- Refcount leak on delete → GC with delayed reclamation
- Scale: namespace shard; chunk store by hash prefix; separate notification fan-out service

## Interview trigger phrase

> “I'd sync **chunk hashes**, upload only missing chunks, and detect conflicts with **parent revision** — binaries get conflict copies; collab text is a different consistency model.”

## Exercise

1. Two devices edit `resume.pdf` offline, then reconnect — exact conflict UX and data model fields involved.
2. Why content-defined chunking beats fixed 4 MB when a user inserts 1 byte at the start of a 2 GB video.
3. How does sharing a folder with 10k viewers change the sync fan-out design?
