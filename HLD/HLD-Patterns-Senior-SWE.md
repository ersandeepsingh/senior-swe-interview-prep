# HLD / System-Design Pattern Playbook — Senior SWE Interview Prep

Organized by **category → concept/pattern → 1-line intent + where it shows up**.
HLD rounds test whether you can turn fuzzy requirements into a scalable, available, consistent architecture and defend the trade-offs. Each classic design problem is mapped to its **most critical** concept (the crux the interviewer is really probing), not every building block it touches.

Legend: 🟢 warm-up · 🟡 standard 45–60 min · 🔴 hard / senior-signal

---

## 1. Foundational Concepts (the vocabulary every answer leans on)

Deep-dives: [`01-Foundational-Concepts/`](01-Foundational-Concepts/README.md)

- **[CAP theorem](01-Foundational-Concepts/01_cap_theorem.md)** — Pick 2 of Consistency/Availability/Partition-tolerance → why a system chooses AP or CP under a partition.
- **[PACELC](01-Foundational-Concepts/02_pacelc.md)** — Else (no partition) trade latency vs consistency → Dynamo (PA/EL) vs. spanner (PC/EC).
- **[Consistency models](01-Foundational-Concepts/03_consistency_models.md)** — Strong / eventual / causal / read-your-writes → session guarantees in a social feed.
- **[Latency vs throughput](01-Foundational-Concepts/04_latency_vs_throughput.md)** — Response time vs. requests served → optimize p99 vs. QPS.
- **[Availability math](01-Foundational-Concepts/05_availability_math.md)** — Nines, SLA/SLO/SLI → 99.99% ≈ 52 min/yr downtime budget.
- **[Back-of-envelope estimation](01-Foundational-Concepts/06_back_of_envelope.md)** — QPS, storage, bandwidth sizing → "1B users, 2 posts/day → X writes/s."
- **[Vertical vs horizontal scaling](01-Foundational-Concepts/07_vertical_vs_horizontal.md)** — Scale up vs scale out → why we shard instead of buying a bigger box.
- **[Stateless vs stateful services](01-Foundational-Concepts/08_stateless_vs_stateful.md)** — Push state to stores → enable easy horizontal scaling.

## 2. Networking & Traffic Management

- **Load balancing** — Distribute traffic (L4 vs L7, round-robin/least-conn/consistent-hash) → front any tier.
- **Reverse proxy / API gateway** — Single entry: routing, auth, throttling → microservices front door.
- **DNS & GeoDNS** — Name resolution + geo-routing → route users to nearest region.
- **CDN** — Edge-cache static/media near users → images, video, JS bundles.
- **Rate limiting / throttling** — Token bucket / sliding window → protect APIs from abuse.
- **Backpressure & load shedding** — Drop/delay under overload → shed low-priority traffic first.
- **Connection handling** — Keep-alive, connection pooling, WebSockets → real-time channels.

## 3. Data Storage & Modeling

- **SQL vs NoSQL choice** — Relational vs document/column/KV/graph → pick by access pattern & consistency need.
- **Indexing** — B-tree / hash / inverted index → speed reads, cost writes.
- **Normalization vs denormalization** — Joins vs read-optimized duplication → denormalize a feed for fast reads.
- **Data partitioning / sharding** — Range / hash / directory / geo sharding → split a huge users table.
- **Consistent hashing** — Minimize reshuffling on node change → distributed cache / DB ring.
- **Replication** — Leader-follower / multi-leader / leaderless → read scaling + failover.
- **Read/write splitting** — Reads to replicas, writes to primary → offload analytics reads.
- **Multi-region / geo-replication** — Data near users, DR → active-active vs active-passive.
- **Time-series / columnar / graph stores** — Specialized engines → metrics (TSDB), analytics (columnar), social graph.
- **Blob / object storage** — Large binaries → S3-style store for media & backups.

## 4. Caching

- **Cache placement** — Client / CDN / app / distributed / DB → layers of a read path.
- **Caching strategies** — Cache-aside / read-through / write-through / write-back → pick by consistency & latency.
- **Eviction policies** — LRU / LFU / TTL → bound memory footprint.
- **Cache invalidation** — Keep cache and source in sync → the classic "hard problem."
- **Hot-key / thundering herd** — Fan-out & stampede control → request coalescing, jittered TTLs.

## 5. Asynchronous Processing & Messaging

- **Message queue** — Decouple producer/consumer, buffer spikes → order processing pipeline.
- **Pub/Sub** — Fan-out events to many subscribers → notify N services on an event.
- **Event streaming (log)** — Durable, replayable ordered log (Kafka-style) → event sourcing, analytics.
- **Delivery semantics** — At-most / at-least / exactly-once → dedup + idempotency keys.
- **Dead-letter queues & retries** — Handle poison messages → backoff + DLQ.
- **CDC (change data capture)** — Stream DB changes downstream → keep search index in sync.
- **Batch vs stream processing** — Bulk vs real-time → nightly ETL vs live aggregation.

## 6. Distributed Systems Coordination

- **Leader election / consensus** — Raft / Paxos / ZooKeeper → pick a primary safely.
- **Distributed locks** — Mutual exclusion across nodes → Redlock, ZK locks (with caveats).
- **Distributed transactions** — 2PC / Saga / TCC → cross-service consistency without a global txn.
- **Idempotency** — Safe retries → idempotency keys on payments.
- **Quorum (R+W>N)** — Tunable consistency in leaderless stores → Dynamo-style reads/writes.
- **Vector clocks / logical clocks** — Order events without global time → conflict detection.
- **Conflict resolution** — LWW / CRDTs → collaborative editing, offline sync.
- **Heartbeats & failure detection** — Detect dead nodes → gossip, health checks.

## 7. Reliability, Resilience & Observability

- **Replication & failover** — Redundancy + automatic promotion → survive node loss.
- **Circuit breaker / bulkhead / timeout** — Contain cascading failures → isolate a failing dependency.
- **Graceful degradation** — Serve reduced functionality → show cached feed when ranker is down.
- **Rate limiting & quotas** — Fairness + protection → per-tenant limits.
- **Monitoring / logging / tracing** — Metrics, logs, distributed traces → the 3 pillars of observability.
- **Disaster recovery** — RPO / RTO, backups, multi-region → recover from region outage.
- **Chaos / fault injection** — Test resilience deliberately → verify failover works.

## 8. Search, Analytics & ML Serving Building Blocks

- **Inverted index / search engine** — Full-text search (Elasticsearch) → product/search autocomplete.
- **Ranking & relevance** — Scoring + ML re-rank → feed/search ordering.
- **OLAP / data warehouse / lake** — Analytical queries at scale → dashboards & reporting.
- **Feature store & model serving** — Low-latency inference → recommendations, personalization.
- **Bloom filters / HyperLogLog / Count-Min** — Probabilistic sketches → dedup, cardinality, heavy hitters.

## 9. Security & Multi-Tenancy

- **AuthN / AuthZ** — OAuth2 / JWT / RBAC → who you are + what you can do.
- **Encryption** — TLS in transit, at rest, KMS → protect sensitive data.
- **API security** — Rate limits, input validation, WAF → guard the edge.
- **Multi-tenancy isolation** — Shared vs isolated data/compute → per-tenant limits & data separation.

---

## 10. Classic HLD Problems — Read-Heavy / Feeds & Social

- **Design a URL Shortener (TinyURL)** — ID generation, KV lookup, cache → *crux: key generation + read caching*. 🟡
- **Design a Pastebin** — Blob storage + metadata + TTL → *crux: object storage + expiry*. 🟡
- **Design Twitter/Instagram Feed** — Fan-out on write vs read, timeline → *crux: fan-out strategy + celebrity problem*. 🔴
- **Design a News Feed / Ranking** — Aggregation + ML ranking → *crux: ranking + caching*. 🔴
- **Design a Social Graph (follow/friend)** — Graph store + adjacency → *crux: graph modeling + sharding*. 🔴
- **Design Search Autocomplete / Typeahead** — Trie + top-K + prefix cache → *crux: trie + ranking at edge*. 🟡

## 11. Classic HLD Problems — Write-Heavy / Real-Time

- **Design a Chat System (WhatsApp/Slack)** — WebSockets, presence, delivery/read receipts → *crux: connection mgmt + message fan-out + ordering*. 🔴
- **Design a Notification System** — Multi-channel, queue, dedup, prefs → *crux: async fan-out + delivery guarantees*. 🟡
- **Design a Rate Limiter (distributed)** — Token bucket in a shared store → *crux: distributed counters + consistency*. 🟡
- **Design a Web Crawler** — Frontier, dedup, politeness, distributed fetch → *crux: work distribution + dedup at scale*. 🔴
- **Design a Metrics/Monitoring System** — Ingest, TSDB, aggregation, alerting → *crux: high-write ingestion + time-series storage*. 🔴
- **Design a Logging/Analytics Pipeline** — Stream ingest → process → store/query → *crux: stream processing + storage tiering*. 🔴

## 12. Classic HLD Problems — Media & Streaming

- **Design YouTube/Netflix (video streaming)** — Upload, transcode, CDN, adaptive bitrate → *crux: CDN + transcoding pipeline*. 🔴
- **Design an Image/File Hosting Service** — Object store + CDN + metadata → *crux: blob storage + edge delivery*. 🟡
- **Design Google Drive/Dropbox** — Sync, chunking, dedup, conflict → *crux: file sync + chunk dedup + conflict resolution*. 🔴
- **Design a Live Streaming platform** — Low-latency ingest + fan-out → *crux: real-time distribution*. 🔴

## 13. Classic HLD Problems — Transactional / Marketplace

- **Design a Payment System / Wallet** — Ledger, idempotency, consistency → *crux: exactly-once + strong consistency*. 🔴
- **Design Ride-Hailing (Uber/Lyft)** — Geo-index matching, pricing, trip state → *crux: geospatial matching + real-time location*. 🔴
- **Design Food Delivery (Swiggy/DoorDash)** — Order + dispatch + tracking → *crux: matching + real-time state*. 🔴
- **Design a Ticket Booking (BookMyShow/Ticketmaster)** — Seat locking, no double-book → *crux: concurrency + strong consistency on inventory*. 🔴
- **Design an E-commerce (Amazon)** — Catalog, cart, inventory, orders → *crux: inventory consistency + read scaling*. 🔴
- **Design a Hotel/Airline Reservation** — Availability + booking + cancellation → *crux: consistency under concurrent booking*. 🔴
- **Design Stock Exchange / Order Matching** — Order book, low-latency matching → *crux: latency + ordering + consistency*. 🔴

## 14. Classic HLD Problems — Infrastructure / Platform

- **Design a Distributed Cache** — Sharding + consistent hashing + eviction → *crux: consistent hashing + invalidation*. 🔴
- **Design a Key-Value Store (Dynamo)** — Partitioning, replication, quorum → *crux: consistent hashing + tunable consistency*. 🔴
- **Design a Distributed Message Queue (Kafka)** — Partitions, offsets, consumer groups → *crux: durable ordered log + delivery semantics*. 🔴
- **Design a Distributed Unique ID Generator** — Snowflake / range allocation → *crux: uniqueness + ordering without coordination*. 🟡
- **Design a Distributed Job Scheduler** — Cron at scale, leases, retries → *crux: leader election + fault tolerance*. 🔴
- **Design a Distributed File System (GFS/HDFS)** — Chunking, replication, master/chunkservers → *crux: metadata mgmt + replication*. 🔴
- **Design an API Rate Limiter as a Service** — Central quotas across fleet → *crux: distributed counting*. 🟡
- **Design a Config / Feature-Flag Service** — Push updates, versioning → *crux: low-latency reads + propagation*. 🟡

## 15. Classic HLD Problems — Location & Misc

- **Design a Proximity/Nearby service (Yelp)** — Geospatial index (geohash/quadtree) → *crux: geo-indexing*. 🔴
- **Design Google Maps / routing** — Graph + shortest path + tiles → *crux: graph partitioning + precomputation*. 🔴
- **Design a Leaderboard / Ranking** — Sorted set at scale → *crux: real-time ranking + sharding*. 🟡
- **Design an Online Code Judge** — Submission queue + sandboxed execution → *crux: async execution + isolation*. 🟡
- **Design a Recommendation System** — Candidate gen + ranking + serving → *crux: offline compute + low-latency serving*. 🔴

---

## How to run an HLD round (senior playbook)

1. **Requirements (5–8 min):** separate **functional** (features) from **non-functional** (scale, latency, availability, consistency); state assumptions and get buy-in on scope.
2. **Estimate (5 min):** QPS, storage, bandwidth — this justifies later choices (sharding, caching, CDN).
3. **API + data model:** define the core endpoints and the primary entities/tables before drawing boxes.
4. **High-level architecture:** client → LB/gateway → services → data stores → async workers; draw the happy path first.
5. **Deep dive on the crux:** go deep on the 1–2 hardest parts (the mapped "crux" above) — that's where senior signal lives.
6. **Scale & harden:** add caching, sharding, replication, queues; then discuss **failure modes**, consistency trade-offs, bottlenecks, and monitoring.
7. **Trade-offs out loud:** always name what you're giving up (e.g., "eventual consistency here to keep the feed fast").

Highest-ROI problems to drill first: **URL Shortener, Twitter Feed, Chat System, Rate Limiter, YouTube/Netflix, Ticket Booking, Key-Value Store, Notification System** — together they cover nearly every building block above.

Trade-off pairs interviewers love to hear you reason about: **consistency ↔ availability, latency ↔ throughput, read-optimized ↔ write-optimized, normalization ↔ denormalization, strong ↔ eventual consistency, sync ↔ async, cost ↔ performance.**
