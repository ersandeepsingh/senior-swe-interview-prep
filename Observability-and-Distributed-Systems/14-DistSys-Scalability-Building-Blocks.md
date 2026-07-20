# 14 · Distributed Systems — Scalability Building Blocks

> The reusable pieces you assemble to handle growth.

---

## Horizontal vs vertical scaling

**Definition:** **Vertical** scaling = making one machine bigger (more CPU/RAM). **Horizontal** scaling = adding more machines.

**Simple explanation:** Vertical is simplest (no code changes) but has a ceiling and a single point of failure — you can only buy so big a box. Horizontal scales far and adds redundancy, but requires your system to be distributable (stateless services, sharded data, load balancing). Most large systems scale horizontally.

**Example:** A DB running hot: vertical = upgrade from 16→64 cores (buys time, still one box). Horizontal = add read replicas and shard the data across machines (scales indefinitely, survives a node loss).

---

## Stateless services

**Definition:** Services that keep no client/session state in local memory between requests — any instance can handle any request.

**Simple explanation:** If a server remembers things locally (like a logged-in session in memory), you can't freely add/remove servers or load-balance, because a user is "stuck" to one box. Push state to a shared store (DB, Redis) so every instance is interchangeable — then you can scale out and restart freely.

**Example:** Instead of storing sessions in each server's memory, store them in Redis. Now the load balancer can send a user to any of 20 servers, autoscaling can kill and spawn instances anytime, and a crash doesn't log everyone out.

---

## Caching layers & invalidation

**Definition:** Storing frequently accessed data in fast storage closer to the consumer to reduce load and latency — and the hard problem of keeping caches fresh.

**Simple explanation:** Caches (Redis, in-memory, CDN) absorb read load and speed things up dramatically. The difficulty is **invalidation**: when the source data changes, stale cache entries must be updated or expired, or users see old data. Common approaches: TTL expiry, write-through, or event/CDC-driven invalidation.

**Example:** Product prices cached in Redis with a 60s TTL cut DB reads 100x. When a price changes, you either wait for the TTL, or proactively delete the `product:42:price` key on update so the next read repopulates it with the new value.

---

## CDN & edge

**Definition:** Content Delivery Networks cache and serve content from servers geographically close to users (the "edge").

**Simple explanation:** Distance = latency. A CDN puts copies of your static assets (and increasingly dynamic/edge-computed content) in hundreds of locations worldwide, so a user in Tokyo is served from Tokyo, not Virginia. It also shields your origin servers from massive traffic.

**Example:** A video platform serves thumbnails, JS, and video segments from CDN edge nodes. A user in India downloads from a nearby edge (20ms) instead of the US origin (250ms), and the origin only ever serves the CDN a single cache-miss copy.

---

## Load balancing

**Definition:** Distributing incoming traffic across multiple backend instances. Operates at **L4** (transport: IP/port) or **L7** (application: HTTP paths/headers), using algorithms like round-robin, least-connections, or consistent-hash.

**Simple explanation:** A load balancer is the traffic cop in front of your servers. **L4** is fast and simple (routes by connection). **L7** understands HTTP, so it can route `/api` vs `/images` to different pools, do TLS termination, and sticky sessions. Algorithms decide *which* server gets the next request.

**Example:** An L7 load balancer routes `/checkout` to the payments cluster and `/search` to the search cluster, using least-connections so the least-busy instance in each pool gets the next request. Consistent-hash routing can pin a given user to the same backend to improve cache hits.

---

## Bloom filters / HyperLogLog / Count-Min Sketch

**Definition:** Probabilistic data structures that answer set/cardinality/frequency questions using tiny memory, trading exactness for space.

**Simple explanation:** At massive scale, exact counting is too memory-hungry, so you use sketches that are *approximately* right.
- **Bloom filter:** "have I seen this before?" — no false negatives, some false positives, tiny memory.
- **HyperLogLog:** "how many *unique* items?" — counts billions of distinct values in a few KB.
- **Count-Min Sketch:** "how frequent is this item?" — estimates counts of heavy hitters cheaply.

**Example:**
- Bloom filter: before hitting the DB, check "is this username taken?" — if the filter says no, it's definitely free (skip the DB); if yes, verify in the DB.
- HyperLogLog: count unique daily visitors across billions of events in ~12KB instead of storing every visitor ID.
- Count-Min Sketch: find the top trending search terms in a firehose without storing every query.
