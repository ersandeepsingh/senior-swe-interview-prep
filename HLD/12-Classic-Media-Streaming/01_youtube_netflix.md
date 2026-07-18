# Design YouTube / Netflix 🔴

> **Crux:** Move bits cheaply and fast — **transcode once into ABR ladder**, store in object storage, **serve from CDN edge**. Origin cannot take the heat.

## Clarify (say this first)

**Functional**
- Upload video → process → publish; play with seek, pause, quality switch
- Catalog, recommendations, watch history (scope lightly)
- VoD first; live is a different design (see live streaming)

**Non-functional**
- Playback start < 2s; rebuffer rare on typical broadband
- Global viewers; 99.9%+ playback availability
- Cost-sensitive: egress >> compute; cache hit ratio is the KPI
- Consistency: metadata strong enough for publish; playback can be eventual

## Back-of-envelope

- 500M DAU, avg 1 hr watch/day, 5 Mbps avg bitrate → ~**3 Pbps** peak if all concurrent (impossible from origin)
- Reality: heavy CDN; origin only cache-miss + upload
- 1M uploads/day × 1 GB avg raw → 1 PB/day raw; post-transcode ~2–3× storage (ladder)
- Metadata QPS tiny vs chunk GET QPS (billions/day)

## API + data model

```text
POST /videos                  # initiate upload (returns upload_url / session)
PUT  /uploads/{id}/parts      # chunked upload
POST /videos/{id}/publish
GET  /videos/{id}/manifest    # HLS/DASH playlist URL
GET  /play/{video_id}/{seg}   # segment (usually CDN URL, not API)
```

| Entity | Key fields |
|--------|------------|
| Video | id, owner, status, duration, title |
| Asset | video_id, codec, resolution, bitrate, object_key |
| Manifest | video_id, format (hls/dash), cdn_url |
| WatchEvent | user_id, video_id, position, ts (async) |

## High-level architecture

```text
Uploader ──► Upload Svc ──► Object Store (raw)
                 │
                 ▼
            Transcode Q ──► Workers (ABR ladder + thumbnails)
                 │
                 ▼
            Object Store (segments) ──► CDN Edge ──► Player
                 │
            Metadata DB / Search ◄── Catalog / Recs
```

## Deep dive: the crux

**Why ABR + CDN**
- One bitrate = buffer or waste. Ladder (240p…4K) + HLS/DASH lets player adapt.
- Segments (2–10s) are independently cacheable; CDN absorbs geo fan-out.

| Alternative | When to pick |
|-------------|--------------|
| Progressive MP4 from origin | Tiny scale / internal tool |
| Single bitrate + CDN | Live simplicity; poor mobile UX |
| ABR + multi-tier CDN | Consumer VoD at scale (**default**) |
| Peer-assisted / proprietary CDN | Extreme scale + cost (Netflix Open Connect–style) |

**Transcode pipeline:** upload complete → enqueue → parallel encode per rendition → package → write manifests → mark READY. Idempotent jobs; DLQ for poison files.

**Hot video:** CDN origin-shield + cache; hot metadata in Redis; don't shatter origin.

**DRM / signed URLs (mention):** short-lived tokens on manifests/segments; rotate keys; keep auth off the hot chunk path where possible.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Many ABR renditions | Smooth playback | Storage + encode cost |
| Long segment duration | Fewer requests, better cache | Coarser quality switches |
| Push CDN / ISP caches | Egress savings | Capex, less control |
| Async publish | Upload UX fast | Delay before playable |

## Failure modes & scale

- Transcode backlog → priority queues (paid/creator first); degrade to fewer bitrates
- CDN origin storm on miss → shield, soft-TTL, request coalesce
- Corrupt segment → checksum + multi-AZ object store; player failover to next CDN
- Region outage → multi-CDN / multi-region origin
- Scale knobs: shard metadata by video_id; partition encode workers; geo DNS to nearest PoP

## Interview trigger phrase

> “I'd **transcode into an ABR ladder**, store segments in object storage, and put a **CDN** in front — origin only sees uploads and cache misses; playback cost is an edge problem.”

## Exercise

1. Walk through first play of a newly published video before any CDN warm-up — what hits origin?
2. How do you add 4K without rewriting the player contract?
3. Compare VoD architecture to live: what must change for sub-5s glass-to-glass latency?
