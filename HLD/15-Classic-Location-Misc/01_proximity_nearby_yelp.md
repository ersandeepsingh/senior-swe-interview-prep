# Design a Proximity / Nearby Service (Yelp) 🔴

> **Crux:** Answer “what’s near me?” with a **geo-index** (geohash / quadtree / S2) — not a full table scan with Haversine on every request.

## Clarify (say this first)

**Functional**
- Nearby search: lat/lng + radius + filters (category, open now, rating)
- Business CRUD; map pins; pagination / ranked list
- Optional: autocomplete, reviews (scope carefully)

**Non-functional**
- p99 search tens of ms
- Freshness: new/closed businesses in minutes–hours
- Scale: 100M+ POIs; spiky urban density
- Read-heavy; geo queries dominate

## Back-of-envelope

```text
100M businesses; avg 10 searches/user/day; 50M DAU → ~6k QPS avg, 30k+ peak
Result set: top 20 within 5 km
Index: geohash precision ~5–6 (~1–5 km cells) + in-memory/ES docs
Hot cities: NYC cell may hold 100k+ POIs → filter + secondary rank
```

## API + data model

```text
GET /v1/nearby?lat=&lng=&radius_m=&category=&limit=
GET /v1/businesses/{id}
PUT /v1/businesses/{id}   # admin / owner
```

| Entity | Fields |
|--------|--------|
| Business | `id`, `name`, `lat`, `lng`, `geohash`, `cats[]`, `rating` |
| Geo cell | `geohash` → posting list / doc ids |

## High-level architecture

```text
  Mobile / Web
       │
       ▼
  API + Search service
       │
       ├─► Geo index (ES / custom)  geohash / quadtree / S2
       ├─► Business KV / SQL         details, hours
       └─► Ranker (rating, distance, personalization)
```

## Deep dive: the crux

**Geo-indexing:**
| Structure | Idea | When |
|-----------|------|------|
| **Geohash** | Prefix = containing cell; query = center + neighbors | Simple; Redis/ES friendly |
| **Quadtree / R-tree** | Hierarchical spatial split | Adaptive density |
| **S2 / H3** | Sphere cells; better polar/edge behavior | Global maps at scale |

**Query:** encode user point → fetch cell + 8 neighbors (or ring for radius) → filter true distance → rank. **Load imbalance:** dense downtown cells — subdivide (longer geohash) or shard lists. **Pick:** geohash/S2 in search engine; precompute cell; reindex on move/edit.

**Ranking after geo filter:** distance is necessary but not sufficient — blend rating, popularity, open-now, and personalization. Return `next_cursor` over score+id for stable pagination as users pan the map.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Geohash neighbors | Easy mental model | Edge false positives; filter needed |
| Longer precision | Smaller cells | More cells to fan out for large radius |
| Quadtree | Density-adaptive | Harder ops than ES geohash |
| Pure SQL + GIS | Accurate | Scale ceiling without sharding |
| Cache top queries | Latency | Stale pins; key explosion |

## Failure modes & scale

- **Hot cell:** shard posting lists; cache popular downtown queries
- **Radius too large:** cap radius; grid sample; “zoom out” UX
- **Moving POIs (food trucks):** shorter TTL / frequent rehash
- **Stale index:** async indexer from CDC; read-your-writes via primary for owner
- **Multi-region:** geo-partition data by continent/city shard

## Interview trigger phrase

> “I’d index businesses by **geohash/S2 cell**, query the user’s cell plus neighbors, **filter by real distance**, then rank — so nearby never becomes a full scan.”

## Exercise

1. Radius crosses geohash boundaries — why neighbor cells are required.  
2. One cell has 500k restaurants — how do you keep p99 healthy?  
3. Compare geohash vs quadtree for a city with huge density skew.
