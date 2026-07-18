# Design a Live Streaming Platform 🔴

> **Crux:** **Low-latency ingest** from creator, then **real-time fan-out** to millions of viewers — delay budget is seconds, not VoD's minutes.

## Clarify (say this first)

**Functional**
- Creator goes live; viewers join mid-stream; chat/reactions (scope)
- Record-to-VoD after stream (optional)
- Regional events / sports; interactive (sub-3s) vs broadcast (5–15s)

**Non-functional**
- Glass-to-glass latency target (state it): e.g. <5s interactive, <15s casual
- Scale: 1 stream → 1M concurrent viewers (fan-out >> ingest)
- Resilience: packet loss, creator reconnect, PoP failure
- Consistency: all viewers roughly same timeline; chat may lag video slightly

## Back-of-envelope

- 1080p30 ~4–8 Mbps ingest × 100k concurrent lives → ingest cluster sized for peak creators
- 1 popular stream × 1M viewers × 3 Mbps → **3 Tbps** egress → must be CDN/edge, never origin unicast from one box
- GOP / segment duration trades latency vs efficiency (1s segments ≈ lower latency, more overhead)

## API + data model

```text
POST /lives                     # create stream → ingest URL + stream_key
RTMP/WebRTC ──► ingest endpoint
GET  /lives/{id}/playback       # HLS/LL-HLS/DASH or WebRTC URL
POST /lives/{id}/end
WS   /lives/{id}/chat           # optional side channel
```

| Entity | Key fields |
|--------|------------|
| Live | id, creator, status, ingest_region, started_at |
| IngestSession | live_id, codec, bitrate, keyframe_interval |
| Playback | live_id, protocol, cdn_manifest / webrtc_url |
| DVR Window | live_id, retention_sec, object_prefix |

## High-level architecture

```text
Creator ──(RTMP/S RTMPS / WebRTC)──► Ingest Edge (PoP)
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
              Transcode/Packager    Origin Shield         Recording
              (ABR ladder live)          │
                                         ▼
                                   Live CDN / Edge Packagers
                                         │
                                    Viewers (HLS / LL-HLS / WebRTC)
```

## Deep dive: the crux

**Ingest**
- **RTMP/SRT** to nearest ingest PoP; auth via stream key.
- Reconnect: same live_id, resume; short buffer at ingest.

**Fan-out**
- Package to **LL-HLS / LHLS / DASH** for scale; **WebRTC** for ultra-low-latency / interactive (harder at M viewers).
- Multi-tier: ingest → origin → regional edges → clients. Don't unicast from one encoder to N clients.

| Alternative | Latency | Scale | Pick when |
|-------------|---------|-------|-----------|
| Classic HLS (6s parts) | High | Excellent | Casual live, max CDN reuse |
| LL-HLS / CMAF chunked | Mid | Excellent | Sports / product default |
| WebRTC SFU | Lowest | Hard past large N | Co-watch, auctions, interactivity |
| P2P assist | Variable | Helps egress | Cost-sensitive mega-events |

**Transcode live:** parallel renditions at packager tier; failover encoder on health check.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Shorter segments / partial segments | Lower latency | More requests, worse cache efficiency |
| WebRTC to all | Snappy UX | Expensive SFU mesh / regional limits |
| HLS + CDN | Cheap huge fan-out | Higher delay |
| Multi-region active ingest | Creator QoS | Sync complexity for one timeline |

## Failure modes & scale

- Creator network blip → reconnect + freeze-last-frame; don't end stream immediately
- Hot stream → pre-warm edges; origin shield; capacity reservations for events
- Encoder crash → hot standby; viewers may see brief quality drop
- Chat vs video desync → timestamp chat to media timeline
- Scale knobs: geo DNS ingest; shard chat; separate control plane from media plane

## Interview trigger phrase

> “Ingest to the nearest PoP, package for **low-latency HLS** (or WebRTC if interactive), and **fan out via CDN tiers** — one stream's egress problem is an edge distribution problem, not an API problem.”

## Exercise

1. Target 2s glass-to-glass for a live auction — which protocol stack and where do you sacrifice scale?
2. A mega cricket final: how do you capacity-plan CDN vs origin the week before?
3. Creator switches networks mid-stream — what does reconnect look like end-to-end?
