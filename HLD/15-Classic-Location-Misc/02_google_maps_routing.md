# Design Google Maps / Routing 🔴

> **Crux:** Road network as a **huge graph** — you can’t Dijkstra the world per request; use **partitioning + precomputation** (contraction hierarchies / hub labels / tiles) for fast routes and map render.

## Clarify (say this first)

**Functional**
- Route A→B (driving); ETA; alternate routes
- Map tile rendering / pan-zoom
- Traffic-aware ETA (optional deep dive)
- Place search (scope out if needed)

**Non-functional**
- Route p99 &lt; ~100–300 ms
- Global coverage; update roads/traffic continuously
- Offline tiles / cache at edge
- Massive read QPS on tiles; fewer but heavier route QPS

## Back-of-envelope

```text
Road graph: tens of millions nodes/edges (country); billions globally
Naive Dijkstra worldwide: too slow / too much RAM
Tile QPS: 100k+; CDN absorbs most
Route QPS: 1k–10k; CPU heavy → dedicated routers
Precompute: CH preprocessing hours–days offline; query ms
```

## API + data model

```text
GET /directions?origin=&destination=&mode=drive
GET /tiles/{z}/{x}/{y}.pbf
GET /eta?origin=&destination=   # optional
```

| Entity | Role |
|--------|------|
| Node / edge | intersection, road segment, speed, turn costs |
| Tile | vector geometry at zoom `z` |
| Partition / overlay | hierarchy for fast SP |

## High-level architecture

```text
  Client
    ├─ map tiles ◄── CDN ◄── Tile service ◄── tile store
    └─ directions ──► API ──► Routing service
                              │
                              ├─ static graph shards (by region)
                              ├─ traffic overlay (stream updates)
                              └─ precomputed hierarchy (CH / HL)
```

## Deep dive: the crux

**Graph partitioning + precomputation:**
| Technique | Idea | When |
|-----------|------|------|
| **Region shards** | Cut graph by geography; route intra/inter | Operational scale-out |
| **Contraction Hierarchies** | Pre-order shortcuts; bidirectional search | Classic interview pick |
| **Transit Node / Hub labels** | Long-distance via hubs | Very fast LD queries |
| **A\* + landmarks** | Heuristic guided search | Simpler; decent latency |
| **Online Dijkstra only** | Exact on small graph | City-size demos only |

**Traffic:** keep base topology; overlay live speeds on edges; invalidate or partially rebuild affected hierarchy regions. **Tiles:** pyramid zoom levels; CDN; not the same system as routing. **Pick:** geo-partition routers + CH (or A\* for simpler story) + traffic delta stream.

**ETA vs geometry:** path finding returns polylines; ETA applies live speed profiles and turn penalties. Cache short TTL on popular origin–destination pairs; never cache forever under traffic.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Heavy precompute | ms queries | Slow graph updates; build cost |
| Fine partitions | Parallelism | Cross-boundary routing complexity |
| Live traffic | Better ETA | More invalidation / CPU |
| Many alternates | UX | Extra search cost |
| Exact global optimum | Correctness | Latency / cost |

## Failure modes & scale

- **Graph update** (new road): rebuild region; version graphs; sticky clients mid-route
- **Traffic spike incident:** flood updates — batch overlays; degrade to static speeds
- **Hot city routers:** scale partition replicas; cache popular OD pairs briefly
- **Cross-continent:** hierarchical: local CH + long-haul backbone
- **Tile storm:** CDN + HTTP cache headers; avoid origin hits

## Interview trigger phrase

> “The road network is a **partitioned graph** with **precomputed shortcuts** (e.g. contraction hierarchies) so routing stays milliseconds — tiles are a separate **CDN-cached** path.”

## Exercise

1. Why naive Dijkstra on a continent graph fails the latency budget.  
2. Accident closes a highway — what do you update first: tiles, edge weights, or hierarchy?  
3. Sketch how you’d route San Francisco → New York with regional shards.
