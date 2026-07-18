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

Deep-dives: [`02-Networking-Traffic/`](02-Networking-Traffic/README.md)

- **[Load balancing](02-Networking-Traffic/01_load_balancing.md)** — Distribute traffic (L4 vs L7, round-robin/least-conn/consistent-hash) → front any tier.
- **[Reverse proxy / API gateway](02-Networking-Traffic/02_reverse_proxy_api_gateway.md)** — Single entry: routing, auth, throttling → microservices front door.
- **[DNS & GeoDNS](02-Networking-Traffic/03_dns_geodns.md)** — Name resolution + geo-routing → route users to nearest region.
- **[CDN](02-Networking-Traffic/04_cdn.md)** — Edge-cache static/media near users → images, video, JS bundles.
- **[Rate limiting / throttling](02-Networking-Traffic/05_rate_limiting.md)** — Token bucket / sliding window → protect APIs from abuse.
- **[Backpressure & load shedding](02-Networking-Traffic/06_backpressure_load_shedding.md)** — Drop/delay under overload → shed low-priority traffic first.
- **[Connection handling](02-Networking-Traffic/07_connection_handling.md)** — Keep-alive, connection pooling, WebSockets → real-time channels.

## 3. Data Storage & Modeling

Deep-dives: [`03-Data-Storage-Modeling/`](03-Data-Storage-Modeling/README.md)

- **[SQL vs NoSQL choice](03-Data-Storage-Modeling/01_sql_vs_nosql.md)** — Relational vs document/column/KV/graph → pick by access pattern & consistency need.
- **[Indexing](03-Data-Storage-Modeling/02_indexing.md)** — B-tree / hash / inverted index → speed reads, cost writes.
- **[Normalization vs denormalization](03-Data-Storage-Modeling/03_normalization_vs_denormalization.md)** — Joins vs read-optimized duplication → denormalize a feed for fast reads.
- **[Data partitioning / sharding](03-Data-Storage-Modeling/04_partitioning_sharding.md)** — Range / hash / directory / geo sharding → split a huge users table.
- **[Consistent hashing](03-Data-Storage-Modeling/05_consistent_hashing.md)** — Minimize reshuffling on node change → distributed cache / DB ring.
- **[Replication](03-Data-Storage-Modeling/06_replication.md)** — Leader-follower / multi-leader / leaderless → read scaling + failover.
- **[Read/write splitting](03-Data-Storage-Modeling/07_read_write_splitting.md)** — Reads to replicas, writes to primary → offload analytics reads.
- **[Multi-region / geo-replication](03-Data-Storage-Modeling/08_multi_region_geo_replication.md)** — Data near users, DR → active-active vs active-passive.
- **[Time-series / columnar / graph stores](03-Data-Storage-Modeling/09_specialized_stores.md)** — Specialized engines → metrics (TSDB), analytics (columnar), social graph.
- **[Blob / object storage](03-Data-Storage-Modeling/10_blob_object_storage.md)** — Large binaries → S3-style store for media & backups.

## 4. Caching

Deep-dives: [`04-Caching/`](04-Caching/README.md)

- **[Cache placement](04-Caching/01_cache_placement.md)** — Client / CDN / app / distributed / DB → layers of a read path.
- **[Caching strategies](04-Caching/02_caching_strategies.md)** — Cache-aside / read-through / write-through / write-back → pick by consistency & latency.
- **[Eviction policies](04-Caching/03_eviction_policies.md)** — LRU / LFU / TTL → bound memory footprint.
- **[Cache invalidation](04-Caching/04_cache_invalidation.md)** — Keep cache and source in sync → the classic "hard problem."
- **[Hot-key / thundering herd](04-Caching/05_hot_key_thundering_herd.md)** — Fan-out & stampede control → request coalescing, jittered TTLs.

## 5. Asynchronous Processing & Messaging

Deep-dives: [`05-Async-Messaging/`](05-Async-Messaging/README.md)

- **[Message queue](05-Async-Messaging/01_message_queue.md)** — Decouple producer/consumer, buffer spikes → order processing pipeline.
- **[Pub/Sub](05-Async-Messaging/02_pubsub.md)** — Fan-out events to many subscribers → notify N services on an event.
- **[Event streaming (log)](05-Async-Messaging/03_event_streaming.md)** — Durable, replayable ordered log (Kafka-style) → event sourcing, analytics.
- **[Delivery semantics](05-Async-Messaging/04_delivery_semantics.md)** — At-most / at-least / exactly-once → dedup + idempotency keys.
- **[Dead-letter queues & retries](05-Async-Messaging/05_dlq_retries.md)** — Handle poison messages → backoff + DLQ.
- **[CDC (change data capture)](05-Async-Messaging/06_cdc.md)** — Stream DB changes downstream → keep search index in sync.
- **[Batch vs stream processing](05-Async-Messaging/07_batch_vs_stream.md)** — Bulk vs real-time → nightly ETL vs live aggregation.

## 6. Distributed Systems Coordination

Deep-dives: [`06-Distributed-Coordination/`](06-Distributed-Coordination/README.md)

- **[Leader election / consensus](06-Distributed-Coordination/01_leader_election_consensus.md)** — Raft / Paxos / ZooKeeper → pick a primary safely.
- **[Distributed locks](06-Distributed-Coordination/02_distributed_locks.md)** — Mutual exclusion across nodes → Redlock, ZK locks (with caveats).
- **[Distributed transactions](06-Distributed-Coordination/03_distributed_transactions.md)** — 2PC / Saga / TCC → cross-service consistency without a global txn.
- **[Idempotency](06-Distributed-Coordination/04_idempotency.md)** — Safe retries → idempotency keys on payments.
- **[Quorum (R+W>N)](06-Distributed-Coordination/05_quorum.md)** — Tunable consistency in leaderless stores → Dynamo-style reads/writes.
- **[Vector clocks / logical clocks](06-Distributed-Coordination/06_vector_logical_clocks.md)** — Order events without global time → conflict detection.
- **[Conflict resolution](06-Distributed-Coordination/07_conflict_resolution.md)** — LWW / CRDTs → collaborative editing, offline sync.
- **[Heartbeats & failure detection](06-Distributed-Coordination/08_heartbeats_failure_detection.md)** — Detect dead nodes → gossip, health checks.

## 7. Reliability, Resilience & Observability

Deep-dives: [`07-Reliability-Observability/`](07-Reliability-Observability/README.md)

- **[Replication & failover](07-Reliability-Observability/01_replication_failover.md)** — Redundancy + automatic promotion → survive node loss.
- **[Circuit breaker / bulkhead / timeout](07-Reliability-Observability/02_circuit_breaker_bulkhead_timeout.md)** — Contain cascading failures → isolate a failing dependency.
- **[Graceful degradation](07-Reliability-Observability/03_graceful_degradation.md)** — Serve reduced functionality → show cached feed when ranker is down.
- **[Rate limiting & quotas](07-Reliability-Observability/04_rate_limiting_quotas.md)** — Fairness + protection → per-tenant limits.
- **[Monitoring / logging / tracing](07-Reliability-Observability/05_monitoring_logging_tracing.md)** — Metrics, logs, distributed traces → the 3 pillars of observability.
- **[Disaster recovery](07-Reliability-Observability/06_disaster_recovery.md)** — RPO / RTO, backups, multi-region → recover from region outage.
- **[Chaos / fault injection](07-Reliability-Observability/07_chaos_fault_injection.md)** — Test resilience deliberately → verify failover works.

## 8. Search, Analytics & ML Serving Building Blocks

Deep-dives: [`08-Search-Analytics-ML/`](08-Search-Analytics-ML/README.md)

- **[Inverted index / search engine](08-Search-Analytics-ML/01_inverted_index_search.md)** — Full-text search (Elasticsearch) → product/search autocomplete.
- **[Ranking & relevance](08-Search-Analytics-ML/02_ranking_relevance.md)** — Scoring + ML re-rank → feed/search ordering.
- **[OLAP / data warehouse / lake](08-Search-Analytics-ML/03_olap_warehouse_lake.md)** — Analytical queries at scale → dashboards & reporting.
- **[Feature store & model serving](08-Search-Analytics-ML/04_feature_store_model_serving.md)** — Low-latency inference → recommendations, personalization.
- **[Bloom filters / HyperLogLog / Count-Min](08-Search-Analytics-ML/05_probabilistic_sketches.md)** — Probabilistic sketches → dedup, cardinality, heavy hitters.

## 9. Security & Multi-Tenancy

Deep-dives: [`09-Security-Multi-Tenancy/`](09-Security-Multi-Tenancy/README.md)

- **[AuthN / AuthZ](09-Security-Multi-Tenancy/01_authn_authz.md)** — OAuth2 / JWT / RBAC → who you are + what you can do.
- **[Encryption](09-Security-Multi-Tenancy/02_encryption.md)** — TLS in transit, at rest, KMS → protect sensitive data.
- **[API security](09-Security-Multi-Tenancy/03_api_security.md)** — Rate limits, input validation, WAF → guard the edge.
- **[Multi-tenancy isolation](09-Security-Multi-Tenancy/04_multi_tenancy_isolation.md)** — Shared vs isolated data/compute → per-tenant limits & data separation.

---

## 10. Classic HLD Problems — Read-Heavy / Feeds & Social

Deep-dives: [`10-Classic-Feeds-Social/`](10-Classic-Feeds-Social/README.md)

- **[Design a URL Shortener (TinyURL)](10-Classic-Feeds-Social/01_url_shortener.md)** — ID generation, KV lookup, cache → *crux: key generation + read caching*. 🟡
- **[Design a Pastebin](10-Classic-Feeds-Social/02_pastebin.md)** — Blob storage + metadata + TTL → *crux: object storage + expiry*. 🟡
- **[Design Twitter/Instagram Feed](10-Classic-Feeds-Social/03_twitter_instagram_feed.md)** — Fan-out on write vs read, timeline → *crux: fan-out strategy + celebrity problem*. 🔴
- **[Design a News Feed / Ranking](10-Classic-Feeds-Social/04_news_feed_ranking.md)** — Aggregation + ML ranking → *crux: ranking + caching*. 🔴
- **[Design a Social Graph (follow/friend)](10-Classic-Feeds-Social/05_social_graph.md)** — Graph store + adjacency → *crux: graph modeling + sharding*. 🔴
- **[Design Search Autocomplete / Typeahead](10-Classic-Feeds-Social/06_search_autocomplete.md)** — Trie + top-K + prefix cache → *crux: trie + ranking at edge*. 🟡

## 11. Classic HLD Problems — Write-Heavy / Real-Time

Deep-dives: [`11-Classic-Write-Heavy-Realtime/`](11-Classic-Write-Heavy-Realtime/README.md)

- **[Design a Chat System (WhatsApp/Slack)](11-Classic-Write-Heavy-Realtime/01_chat_system.md)** — WebSockets, presence, delivery/read receipts → *crux: connection mgmt + message fan-out + ordering*. 🔴
- **[Design a Notification System](11-Classic-Write-Heavy-Realtime/02_notification_system.md)** — Multi-channel, queue, dedup, prefs → *crux: async fan-out + delivery guarantees*. 🟡
- **[Design a Rate Limiter (distributed)](11-Classic-Write-Heavy-Realtime/03_distributed_rate_limiter.md)** — Token bucket in a shared store → *crux: distributed counters + consistency*. 🟡
- **[Design a Web Crawler](11-Classic-Write-Heavy-Realtime/04_web_crawler.md)** — Frontier, dedup, politeness, distributed fetch → *crux: work distribution + dedup at scale*. 🔴
- **[Design a Metrics/Monitoring System](11-Classic-Write-Heavy-Realtime/05_metrics_monitoring.md)** — Ingest, TSDB, aggregation, alerting → *crux: high-write ingestion + time-series storage*. 🔴
- **[Design a Logging/Analytics Pipeline](11-Classic-Write-Heavy-Realtime/06_logging_analytics_pipeline.md)** — Stream ingest → process → store/query → *crux: stream processing + storage tiering*. 🔴

## 12. Classic HLD Problems — Media & Streaming

Deep-dives: [`12-Classic-Media-Streaming/`](12-Classic-Media-Streaming/README.md)

- **[Design YouTube/Netflix (video streaming)](12-Classic-Media-Streaming/01_youtube_netflix.md)** — Upload, transcode, CDN, adaptive bitrate → *crux: CDN + transcoding pipeline*. 🔴
- **[Design an Image/File Hosting Service](12-Classic-Media-Streaming/02_image_file_hosting.md)** — Object store + CDN + metadata → *crux: blob storage + edge delivery*. 🟡
- **[Design Google Drive/Dropbox](12-Classic-Media-Streaming/03_google_drive_dropbox.md)** — Sync, chunking, dedup, conflict → *crux: file sync + chunk dedup + conflict resolution*. 🔴
- **[Design a Live Streaming platform](12-Classic-Media-Streaming/04_live_streaming.md)** — Low-latency ingest + fan-out → *crux: real-time distribution*. 🔴

## 13. Classic HLD Problems — Transactional / Marketplace

Deep-dives: [`13-Classic-Transactional-Marketplace/`](13-Classic-Transactional-Marketplace/README.md)

- **[Design a Payment System / Wallet](13-Classic-Transactional-Marketplace/01_payment_wallet.md)** — Ledger, idempotency, consistency → *crux: exactly-once + strong consistency*. 🔴
- **[Design Ride-Hailing (Uber/Lyft)](13-Classic-Transactional-Marketplace/02_ride_hailing.md)** — Geo-index matching, pricing, trip state → *crux: geospatial matching + real-time location*. 🔴
- **[Design Food Delivery (Swiggy/DoorDash)](13-Classic-Transactional-Marketplace/03_food_delivery.md)** — Order + dispatch + tracking → *crux: matching + real-time state*. 🔴
- **[Design a Ticket Booking (BookMyShow/Ticketmaster)](13-Classic-Transactional-Marketplace/04_ticket_booking.md)** — Seat locking, no double-book → *crux: concurrency + strong consistency on inventory*. 🔴
- **[Design an E-commerce (Amazon)](13-Classic-Transactional-Marketplace/05_ecommerce.md)** — Catalog, cart, inventory, orders → *crux: inventory consistency + read scaling*. 🔴
- **[Design a Hotel/Airline Reservation](13-Classic-Transactional-Marketplace/06_hotel_airline_reservation.md)** — Availability + booking + cancellation → *crux: consistency under concurrent booking*. 🔴
- **[Design Stock Exchange / Order Matching](13-Classic-Transactional-Marketplace/07_stock_exchange.md)** — Order book, low-latency matching → *crux: latency + ordering + consistency*. 🔴

## 14. Classic HLD Problems — Infrastructure / Platform

Deep-dives: [`14-Classic-Infrastructure-Platform/`](14-Classic-Infrastructure-Platform/README.md)

- **[Design a Distributed Cache](14-Classic-Infrastructure-Platform/01_distributed_cache.md)** — Sharding + consistent hashing + eviction → *crux: consistent hashing + invalidation*. 🔴
- **[Design a Key-Value Store (Dynamo)](14-Classic-Infrastructure-Platform/02_key_value_store_dynamo.md)** — Partitioning, replication, quorum → *crux: consistent hashing + tunable consistency*. 🔴
- **[Design a Distributed Message Queue (Kafka)](14-Classic-Infrastructure-Platform/03_distributed_message_queue_kafka.md)** — Partitions, offsets, consumer groups → *crux: durable ordered log + delivery semantics*. 🔴
- **[Design a Distributed Unique ID Generator](14-Classic-Infrastructure-Platform/04_unique_id_generator.md)** — Snowflake / range allocation → *crux: uniqueness + ordering without coordination*. 🟡
- **[Design a Distributed Job Scheduler](14-Classic-Infrastructure-Platform/05_distributed_job_scheduler.md)** — Cron at scale, leases, retries → *crux: leader election + fault tolerance*. 🔴
- **[Design a Distributed File System (GFS/HDFS)](14-Classic-Infrastructure-Platform/06_distributed_file_system.md)** — Chunking, replication, master/chunkservers → *crux: metadata mgmt + replication*. 🔴
- **[Design an API Rate Limiter as a Service](14-Classic-Infrastructure-Platform/07_api_rate_limiter_as_service.md)** — Central quotas across fleet → *crux: distributed counting*. 🟡
- **[Design a Config / Feature-Flag Service](14-Classic-Infrastructure-Platform/08_config_feature_flag_service.md)** — Push updates, versioning → *crux: low-latency reads + propagation*. 🟡

## 15. Classic HLD Problems — Location & Misc

Deep-dives: [`15-Classic-Location-Misc/`](15-Classic-Location-Misc/README.md)

- **[Design a Proximity/Nearby service (Yelp)](15-Classic-Location-Misc/01_proximity_nearby_yelp.md)** — Geospatial index (geohash/quadtree) → *crux: geo-indexing*. 🔴
- **[Design Google Maps / routing](15-Classic-Location-Misc/02_google_maps_routing.md)** — Graph + shortest path + tiles → *crux: graph partitioning + precomputation*. 🔴
- **[Design a Leaderboard / Ranking](15-Classic-Location-Misc/03_leaderboard_ranking.md)** — Sorted set at scale → *crux: real-time ranking + sharding*. 🟡
- **[Design an Online Code Judge](15-Classic-Location-Misc/04_online_code_judge.md)** — Submission queue + sandboxed execution → *crux: async execution + isolation*. 🟡
- **[Design a Recommendation System](15-Classic-Location-Misc/05_recommendation_system.md)** — Candidate gen + ranking + serving → *crux: offline compute + low-latency serving*. 🔴

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
