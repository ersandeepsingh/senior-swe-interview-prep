# Engineering Essentials — Senior SWE Interview Prep

The cross-cutting technologies & concepts a senior engineer is expected to speak to fluently — beyond DSA/LLD/HLD and a specific language. Organized by **category → topic → 1-line "what to know."**

The ⭐ marks topics that come up most often in senior interviews and design discussions.

Legend: 🟢 know the basics · 🟡 be able to use & compare · 🔴 be able to design/defend trade-offs · ⭐ high-frequency

Deep-dives (plain English + examples + trade-offs + exercise) live in numbered folders next to this map:

| # | Section | Folder |
|---|---------|--------|
| 1 | API & Communication | [01-API-Communication/](01-API-Communication/README.md) |
| 2 | HTTP & Web Protocols | [02-HTTP-Protocols/](02-HTTP-Protocols/README.md) |
| 3 | Databases — Relational | [03-Databases-Relational/](03-Databases-Relational/README.md) |
| 4 | Databases — NoSQL | [04-Databases-NoSQL/](04-Databases-NoSQL/README.md) |
| 5 | Search & Text | [05-Search-Text/](05-Search-Text/README.md) |
| 6 | Caching | [06-Caching/](06-Caching/README.md) |
| 7 | Messaging & Streaming | [07-Messaging-Streaming/](07-Messaging-Streaming/README.md) |
| 8 | Cloud, Infra & Deployment | [08-Cloud-Infra/](08-Cloud-Infra/README.md) |
| 9 | Security | [09-Security/](09-Security/README.md) |
| 10 | Observability & Reliability | [10-Observability-Reliability/](10-Observability-Reliability/README.md) |
| 11 | Architecture & Design Patterns | [11-Architecture-Patterns/](11-Architecture-Patterns/README.md) |
| 12 | Networking & Systems | [12-Networking-Systems/](12-Networking-Systems/README.md) |
| 13 | Data & Practical Engineering | [13-Data-Practical/](13-Data-Practical/README.md) |

---

## 1. API & Communication Styles ⭐

Deep-dives: [01-API-Communication/](01-API-Communication/README.md)

- **REST** — resources, HTTP verbs, statelessness, status codes, idempotency, HATEOAS. 🟡⭐
- **REST maturity & design** — versioning, pagination, filtering, error contracts, richardson maturity. 🔴⭐
- **GraphQL** — single endpoint, schema/types, queries/mutations/subscriptions, resolvers, N+1 & DataLoader. 🔴⭐
- **gRPC / Protobuf** — binary RPC over HTTP/2, IDL, streaming, when it beats REST. 🔴⭐
- **WebSockets** — full-duplex persistent connection, when vs polling/SSE, scaling stateful connections. 🔴⭐
- **Server-Sent Events (SSE)** — one-way server push over HTTP, vs WebSockets. 🟡
- **Long polling / short polling** — real-time approximations and their costs. 🟡
- **Webhooks** — event callbacks, retries, signature verification. 🟡⭐
- **REST vs GraphQL vs gRPC** — the classic "which and why" trade-off discussion. 🔴⭐
- **API gateways & BFF** — routing, auth, rate limiting, backend-for-frontend pattern. 🔴

## 2. HTTP & Web Protocols ⭐

Deep-dives: [02-HTTP-Protocols/](02-HTTP-Protocols/README.md)

- **HTTP/1.1 vs HTTP/2 vs HTTP/3 (QUIC)** — multiplexing, head-of-line blocking, UDP-based transport. 🔴⭐
- **HTTP methods & semantics** — safe vs idempotent, PUT vs PATCH vs POST. 🟡⭐
- **Status codes** — 2xx/3xx/4xx/5xx meanings, 429, 503, retry semantics. 🟢⭐
- **Headers** — caching (`Cache-Control`, `ETag`), CORS, content negotiation, compression. 🟡⭐
- **Cookies & sessions** — session vs token auth, SameSite, HttpOnly, Secure. 🟡⭐
- **TLS/SSL & HTTPS** — handshake, certificates, mTLS, cert rotation. 🔴⭐
- **DNS** — resolution flow, records (A/AAAA/CNAME/MX), TTL, GeoDNS. 🟡
- **TCP vs UDP** — reliability vs speed, connection setup, when each fits. 🟡⭐

## 3. Databases — Relational ⭐

Deep-dives: [03-Databases-Relational/](03-Databases-Relational/README.md)

- **SQL fundamentals** — joins, group by, subqueries, window functions. 🟡⭐
- **Indexing** — B-tree, composite, covering indexes; when indexes hurt writes. 🔴⭐
- **Query optimization** — `EXPLAIN`/query plans, avoiding full scans, N+1. 🔴⭐
- **ACID & transactions** — atomicity/consistency/isolation/durability. 🟡⭐
- **Isolation levels** — read-uncommitted → serializable; dirty/phantom reads. 🔴⭐
- **Normalization vs denormalization** — forms and when to break them. 🟡⭐
- **Locking & MVCC** — pessimistic vs optimistic, deadlocks. 🔴
- **Connection pooling** — why and how (PgBouncer-style). 🟡
- **Schema migrations** — safe online migrations, backward compatibility. 🔴⭐

## 4. Databases — NoSQL & Specialized ⭐

Deep-dives: [04-Databases-NoSQL/](04-Databases-NoSQL/README.md)

- **Key-Value (Redis, DynamoDB)** — access patterns, when KV beats relational. 🟡⭐
- **Document (MongoDB)** — flexible schema, embedding vs referencing. 🟡
- **Wide-column (Cassandra, HBase)** — partition/clustering keys, write-optimized. 🔴
- **Graph (Neo4j)** — relationship-heavy queries, traversals. 🟡
- **Time-series (InfluxDB, Prometheus)** — metrics, downsampling, retention. 🟡
- **SQL vs NoSQL** — choosing by consistency, scale, and access pattern. 🔴⭐
- **Partitioning/sharding & replication** — horizontal scaling of data. 🔴⭐
- **Consistency models** — strong vs eventual, quorum reads/writes. 🔴⭐

## 5. Search & Text ⭐

Deep-dives: [05-Search-Text/](05-Search-Text/README.md)

- **Elasticsearch / OpenSearch** — inverted index, analyzers, mapping, sharding. 🔴⭐
- **Full-text search concepts** — tokenization, stemming, relevance (TF-IDF/BM25). 🟡⭐
- **Querying** — bool queries, filters vs queries, aggregations. 🟡
- **When to use a search engine vs DB `LIKE`** — the core trade-off. 🟡⭐
- **Autocomplete / typeahead** — edge n-grams, completion suggesters. 🟡
- **Vector search / embeddings** — semantic search, ANN indexes (modern must-know). 🔴⭐
- **Keeping search in sync** — CDC / dual writes / reindexing strategies. 🔴

## 6. Caching ⭐

Deep-dives: [06-Caching/](06-Caching/README.md)

- **Redis / Memcached** — in-memory stores, data structures, use cases. 🟡⭐
- **Caching strategies** — cache-aside, read/write-through, write-back. 🔴⭐
- **Eviction & TTL** — LRU/LFU, expiry, memory bounds. 🟡⭐
- **Cache invalidation** — the hard problem; staleness vs freshness. 🔴⭐
- **Distributed caching** — consistent hashing, hot keys, stampede/thundering herd. 🔴⭐
- **CDN caching** — edge caching for static/media, cache headers. 🟡⭐
- **Redis beyond cache** — pub/sub, rate limiting, locks, leaderboards, streams. 🔴

## 7. Messaging & Streaming ⭐

Deep-dives: [07-Messaging-Streaming/](07-Messaging-Streaming/README.md)

- **Message queues (RabbitMQ, SQS)** — decoupling, work queues, DLQs. 🟡⭐
- **Event streaming (Kafka)** — partitions, offsets, consumer groups, retention, replay. 🔴⭐
- **Pub/Sub** — fan-out to multiple consumers. 🟡⭐
- **Delivery semantics** — at-most/at-least/exactly-once, idempotent consumers. 🔴⭐
- **Ordering & partitioning** — per-key ordering guarantees. 🔴
- **Event-driven architecture** — choreography vs orchestration, event sourcing, CQRS. 🔴⭐
- **Backpressure & DLQ handling** — poison messages, retries with backoff. 🟡

## 8. Cloud, Infra & Deployment ⭐

Deep-dives: [08-Cloud-Infra/](08-Cloud-Infra/README.md)

- **Containers (Docker)** — images, layers, Dockerfile best practices. 🟡⭐
- **Kubernetes** — pods/deployments/services, scaling, config/secrets, ingress. 🔴⭐
- **CI/CD** — pipelines, build/test/deploy, blue-green & canary releases. 🟡⭐
- **Infrastructure as Code** — Terraform/CloudFormation, immutable infra. 🟡
- **Cloud primitives (AWS/GCP/Azure)** — compute, object storage, managed DBs, queues, load balancers. 🟡⭐
- **Serverless / FaaS** — Lambda, cold starts, when it fits. 🟡
- **Load balancing** — L4 vs L7, algorithms, health checks. 🟡⭐
- **Auto-scaling** — horizontal vs vertical, metrics-driven scaling. 🟡
- **Service mesh** — Istio/Envoy, sidecar proxies, mTLS, traffic control. 🔴

## 9. Security ⭐

Deep-dives: [09-Security/](09-Security/README.md)

- **AuthN vs AuthZ** — identity vs permissions. 🟡⭐
- **OAuth 2.0 / OIDC** — flows, tokens, scopes, third-party auth. 🔴⭐
- **JWT** — structure, signing, expiry, refresh tokens, pitfalls. 🟡⭐
- **RBAC / ABAC** — role- vs attribute-based access control. 🟡
- **OWASP Top 10** — injection, XSS, CSRF, SSRF, broken auth. 🔴⭐
- **Encryption** — symmetric/asymmetric, hashing vs encryption, at-rest vs in-transit, KMS. 🟡⭐
- **Secrets management** — Vault, rotation, never in code. 🟡⭐
- **Rate limiting & DDoS protection** — throttling, WAF. 🟡
- **Input validation & sanitization** — trust boundaries. 🟡⭐

## 10. Observability & Reliability ⭐

Deep-dives: [10-Observability-Reliability/](10-Observability-Reliability/README.md)

- **Logging** — structured logs, levels, correlation IDs, centralization (ELK). 🟡⭐
- **Metrics** — RED/USE methods, Prometheus, dashboards (Grafana). 🟡⭐
- **Distributed tracing** — spans, trace context, OpenTelemetry, Jaeger. 🔴⭐
- **Alerting & on-call** — SLI/SLO/SLA, error budgets, alert fatigue. 🔴⭐
- **Resilience patterns** — retries, timeouts, circuit breaker, bulkhead, backoff+jitter. 🔴⭐
- **Graceful degradation & failover** — partial functionality under failure. 🔴
- **Incident response & postmortems** — blameless RCA, mitigation. 🟡⭐
- **Chaos engineering** — deliberate fault injection. 🔴

## 11. Architecture & Design Patterns ⭐

Deep-dives: [11-Architecture-Patterns/](11-Architecture-Patterns/README.md)

- **Monolith vs microservices** — trade-offs, when to split, distributed complexity. 🔴⭐
- **Service boundaries & DDD** — bounded contexts, aggregates. 🔴
- **API contracts & versioning** — backward/forward compatibility. 🔴⭐
- **Saga / distributed transactions** — managing consistency across services. 🔴⭐
- **CQRS & event sourcing** — read/write separation, event log as source of truth. 🔴
- **Idempotency & exactly-once** — safe retries in distributed systems. 🔴⭐
- **12-factor app** — config, statelessness, disposability. 🟡⭐
- **Feature flags** — progressive rollout, kill switches. 🟡

## 12. Networking & Systems Foundations

Deep-dives: [12-Networking-Systems/](12-Networking-Systems/README.md)

- **OSI / TCP-IP model** — layers and where things live. 🟡
- **Firewalls, NAT, VPN, proxies** — network boundaries. 🟡
- **Load balancer vs reverse proxy vs API gateway** — overlapping but distinct roles. 🟡⭐
- **Latency numbers every engineer should know** — memory vs disk vs network orders of magnitude. 🔴⭐
- **Idempotency & retries at the network layer** — dealing with unreliable networks. 🟡
- **Rate limiting algorithms** — token bucket, leaky bucket, sliding window. 🟡⭐

## 13. Data & Practical Engineering

Deep-dives: [13-Data-Practical/](13-Data-Practical/README.md)

- **Serialization formats** — JSON, Protobuf, Avro, MessagePack; schema evolution. 🟡⭐
- **Batch vs stream processing** — ETL/ELT, Spark, real-time pipelines. 🔴
- **Data warehouse vs lake vs lakehouse** — OLTP vs OLAP separation. 🟡
- **Backups & disaster recovery** — RPO/RTO, replication, restore drills. 🔴
- **Git & version control** — branching strategies, rebasing, PR workflow. 🟢⭐
- **Testing strategy** — unit/integration/e2e, test pyramid, contract testing. 🟡⭐

---

## How to prioritize (senior SWE)

1. **Expect deep questions on:** REST/GraphQL/gRPC trade-offs, HTTP & TLS, SQL indexing/transactions/isolation, caching strategies & invalidation, Kafka/messaging semantics, OAuth/JWT, observability (logging/metrics/tracing), resilience patterns, microservices trade-offs.
2. **Strong senior differentiators:** exactly-once/idempotency, event-driven architecture (CQRS/event sourcing/saga), Elasticsearch + vector search, HTTP/2-3, service mesh, distributed tracing, schema evolution.
3. **Know-the-basics, comparison-level:** cloud primitives, Kubernetes, CI/CD, serverless, NoSQL families, security fundamentals (OWASP), IaC.

The senior signal isn't naming these — it's **reasoning about trade-offs**: REST vs gRPC for internal services, SQL vs NoSQL for an access pattern, cache-aside vs write-through, at-least-once vs exactly-once, sync vs async, strong vs eventual consistency. For each essential above, be able to say *when you'd reach for it, what you'd give up, and how it fails.*
