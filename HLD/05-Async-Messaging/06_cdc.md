# Change Data Capture (CDC)

> **CDC** streams **database changes** (insert/update/delete) as events so other systems stay in sync — search indexes, caches, warehouses — **without** dual-writes from the app that drift out of sync.

## Plain English

Dual-write problem: app writes Postgres *and* Elasticsearch in one request. One succeeds, one fails → permanent inconsistency.

CDC: app writes **only the DB**. A CDC connector reads the **WAL / binlog / oplog** and emits change events.

```text
  App ──write──► Primary DB
                    │
                    │ WAL / binlog
                    ▼
               CDC connector
                    │
                    ▼
               Stream / queue
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Search    Cache     Warehouse
```

## Simple example

Product catalog: price update in Postgres.

```text
  UPDATE products SET price=999 WHERE id=42;

  CDC event:
  { op: "U", table: "products", id: 42, price: 999, ts: ... }

  → Elasticsearch doc 42 updated
  → Redis cache key product:42 invalidated or refreshed
```

Checkout code never imports the search client. New sink (e.g. recommendations) taps the same change stream later.

## Why prefer one over the other

| Prefer **CDC** when… | Prefer **app dual-write / explicit events** when… |
|----------------------|-----------------------------------------------------|
| DB is source of truth; many derived stores | You already emit domain events in an outbox |
| You must avoid dual-write drift | Change must include business context DB rows lack |
| Syncing search, cache, analytics from OLTP | Tiny system; one writer; dual-write is acceptable risk |

**Outbox vs CDC:** Outbox = app writes event row in same DB txn, then relay publishes. CDC = read from log. Both beat naïve dual-write. Outbox carries richer domain events; CDC is great for “row changed” sync.

**Ordering caveat:** CDC order follows commit/log order — design sinks to be idempotent; don’t assume perfect “business timeline” without keys and versions.

### Real systems (interview name-drops)

- **Debezium, AWS DMS, DynamoDB Streams, Mongo change streams**.
- Downstream: Elasticsearch, OpenSearch, Snowflake via Kafka Connect.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| CDC from WAL | Single write path; lower drift | Lag; schema/change filtering complexity |
| Dual-write from app | Simple to draw | Partial failure → inconsistency |
| Transactional outbox | Atomic “state + event” | Extra table + publisher process |
| Sync update search in request | Immediate read-your-write | Couples API to search availability |

**Common interview trap:** “We’ll update DB and Elastic in the API” with no failure story.

## Interview trigger phrase

> “I’d treat the DB as source of truth and use **CDC** to feed search and cache — avoids dual-write inconsistency when one hop fails.”

## Exercise

**Design “users table → Elasticsearch user search.”**

1. Why is dual-write from the signup API risky? Give one failure sequence.  
2. Where does CDC read from, and what does the search indexer consume?  
3. User updates email and immediately searches by new email — how do you talk about lag / read-your-write?
