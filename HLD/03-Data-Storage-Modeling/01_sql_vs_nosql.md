# SQL vs NoSQL

> Pick the store from the **access pattern**, not from fashion. SQL wins when you need relations + transactions; NoSQL wins when you need flexible scale or a shape that matches how you read.

## Plain English

| Family | Shape | Typical win |
|--------|-------|-------------|
| **Relational (SQL)** | Tables + joins + ACID | Complex queries, strong invariants |
| **Document** | JSON/BSON docs | Nested objects read/written together |
| **Wide-column** | Row key → column families | Huge write/scan by key range |
| **Key-value** | `get(key)` / `put(key)` | Hot lookups, sessions, cache |
| **Graph** | Nodes + edges | Friend-of-friend, recommendations |

```text
  Access pattern first
           │
           ▼
  ┌────────────────────┐
  │ Need joins + ACID  │──yes──► Postgres / MySQL
  │ across entities?   │
  └─────────┬──────────┘
            │ no
            ▼
  ┌────────────────────┐
  │ Whole object by ID │──yes──► Document (Mongo…)
  │ or flexible schema?│
  └─────────┬──────────┘
            │ no
            ▼
  KV / wide-column / graph (match the query shape)
```

## Simple example

**E-commerce checkout vs product catalog browse.**

| Path | Pattern | Sensible store |
|------|---------|----------------|
| Place order (stock + payment + order row) | Multi-row transaction | **SQL** |
| Product page by `productId` | Fetch one nested doc | **Document** or SQL |
| Session / cart by `userId` | Point lookup | **KV** (Redis) |
| “People also bought” | Multi-hop edges | **Graph** (or precomputed SQL) |

```text
  Checkout (CP + ACID)              Browse (scale + flexible)
  ┌──────────────────┐              ┌──────────────────┐
  │ orders, stock,   │              │ product JSON     │
  │ payments in SQL  │              │ or cache layer   │
  └──────────────────┘              └──────────────────┘
```

## Why prefer one over the other

| Prefer **SQL** when… | Prefer **NoSQL** when… |
|----------------------|------------------------|
| Invariants across tables (money, inventory) | Access is mostly by primary key / known pattern |
| Ad-hoc analytics / reporting joins | Schema evolves fast; nested docs are natural |
| Team already strong at relational modeling | You need easy horizontal partition by key |

**Not “NoSQL scales, SQL doesn’t.”** Postgres shards and replicas scale far. NoSQL shines when the **query shape is simple and fixed** and you want operational simplicity at huge keyspace.

### Real systems (interview name-drops)

- **SQL:** Postgres, MySQL, Aurora, CockroachDB (distributed SQL).
- **Document:** MongoDB, DynamoDB (item model), Firestore.
- **Wide-column:** Cassandra, Bigtable, Scylla.
- **KV:** Redis, Memcached, DynamoDB (as KV), etcd.
- **Graph:** Neo4j, Amazon Neptune.

## Trade-offs

| Choice | You gain | You give up |
|--------|----------|-------------|
| SQL + joins | Correctness, flexible queries | Harder horizontal scale; join cost at high QPS |
| Document by ID | Fast reads of whole object | Cross-doc transactions awkward; duplication |
| Wide-column | Massive write throughput | Modeling is hard; secondary queries limited |
| Pure KV | Simple, fast | Almost no query model beyond the key |
| Graph DB | Natural multi-hop | Overkill if hops are rare / precomputable |

**Common interview trap:** “We’ll use Mongo because it’s web scale.” Seniors say: *“Checkout stays in Postgres; sessions in Redis; feed timeline in Cassandra.”*

## Interview trigger phrase

> “I’d start from access patterns — **SQL for transactional checkout**, **document/KV for product-by-id and sessions**, and only add a specialized store if the query shape demands it.”

## Exercise

**Design storage for a social network MVP.**

1. Pick a store type for: user profile, follow graph, home timeline, and like counters — and say why in one line each.  
2. Where would you *refuse* document DB even if the frontend sends JSON?  
3. One sentence to the interviewer on how you’d evolve from one Postgres DB to a polyglot setup without a rewrite.
