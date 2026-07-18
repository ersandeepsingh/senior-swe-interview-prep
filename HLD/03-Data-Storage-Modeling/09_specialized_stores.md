# Specialized Stores

> When access is **time-ordered metrics**, **analytical scans**, or **multi-hop relationships**, a general OLTP DB fights you. Use **time-series**, **columnar**, or **graph** stores for fit — keep Postgres for the transactional core.

## Plain English

| Store | Optimized for | Not for |
|-------|---------------|---------|
| **Time-series (TSDB)** | Append metrics/events by time; downsampling | Ad-hoc relational joins |
| **Columnar / OLAP** | Scan few columns across billions of rows | High-QPS point updates |
| **Graph** | Traversals (`friend-of-friend`) | Bulk analytics / simple KV |

```text
  Write path                     Read shape
  ──────────                     ──────────
  sensor ticks /sec   ──► TSDB   “CPU p99 last 1h”
  nightly facts       ──► OLAP   “GMV by city, month”
  follow edges        ──► Graph  “people you may know”
  orders / payments   ──► OLTP   ACID checkout
```

## Simple example

**SaaS product with infra metrics + growth analytics + social graph.**

| Data | Store | Why |
|------|-------|-----|
| `cpu{host}` every 10s | Influx / Prometheus / Timescale | Compression, retention, time functions |
| Order facts for BI | BigQuery / Snowflake / Redshift | Columnar scans, cheap aggregations |
| Follows / blocks | Neo4j or edge tables + careful SQL | Multi-hop without join explosion |
| Billing invoices | Postgres | Transactions |

```text
  App ──► Postgres (source of truth)
       └─► CDC / ETL ──► Warehouse (columnar)
  Agents ──► TSDB
  Social features ──► Graph or denormalized SQL
```

## Why prefer one over the other

| Prefer **TSDB** when… | Prefer **columnar** when… | Prefer **graph** when… |
|-----------------------|---------------------------|------------------------|
| High-ingest time data | Wide analytical queries | Relationship depth > 2–3 |
| Retention / rollups matter | Few updates, many scans | Path / pattern queries |

**Why not put metrics in Postgres forever?** Cardinality + retention blow up storage and kill vacuums; TSDBs compress and expire by design.

**Why not graph DB for every “related to”?** One-hop “user has orders” is a foreign key — graph overhead isn’t free.

**Why not OLAP as the only store?** Columnar engines hate high-frequency single-row updates and point-get latency; they shine on scans, not checkout.

### Real systems (interview name-drops)

- **TSDB:** Prometheus, InfluxDB, TimescaleDB, Amazon Timestream.
- **Columnar:** BigQuery, Snowflake, Redshift, ClickHouse, DuckDB.
- **Graph:** Neo4j, Neptune, JanusGraph; also adjacency lists in Cassandra.

## Trade-offs

| Choice | You gain | You give up |
|--------|----------|-------------|
| Specialized store | 10–100× better for its query shape | Another system to operate; sync/ETL |
| Everything in OLTP | One mental model | Cost and latency walls at scale |
| Warehouse via CDC | Fresh analytics without prod load | Pipeline lag; eventual numbers |
| Graph for social | Natural traversals | Harder ops; overkill if precompute works |

**Common interview trap:** “We’ll store logs and metrics in the same MySQL as users.” Seniors separate **OLTP / OLAP / TSDB** and mention the sync path.

## Interview trigger phrase

> “I’d keep **OLTP in Postgres**, ship events to a **columnar warehouse** for analytics, metrics to a **TSDB**, and only introduce a **graph** store if multi-hop queries are a first-class product path.”

## Exercise

**Design storage for an IoT fleet + mobile social app.**

1. Map: device temperature stream, monthly fleet report, “friends who own device X” — to store types.  
2. Why is ClickHouse a poor primary for charging a subscription?  
3. One sentence on how CDC from Postgres to the warehouse avoids dual-writes in the app.
