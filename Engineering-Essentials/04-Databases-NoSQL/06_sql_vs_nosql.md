# SQL vs NoSQL

> Choose the store by **consistency needs, scale shape, and access patterns** — not by résumé keywords.

## Plain English

The classic senior design fork. Winning answer: a decision matrix with trade-offs — often **polyglot** (Postgres + Redis + search), not one database forever.

## Essentials (must-know for this topic)

### Side-by-side

| | **SQL (relational)** | **NoSQL (family varies)** |
|--|----------------------|---------------------------|
| Model | Tables + relations | KV / document / wide / graph / TS |
| Query | Flexible SQL | Often key/query-specific |
| Transactions | Strong multi-row ACID (typical) | Varies; often single-key or limited |
| Scale | Vertical + careful sharding | Often built for horizontal scale |
| Schema | Strict (migrations) | Flexible or query-driven |

### Decision questions (ask in order)

1. Multi-row transactions & joins needed?  
2. What’s the **primary access pattern**?  
3. How big / how multi-region?  
4. Can the team operate it?

### Quick assignment cheat sheet

| Workload | Lean toward |
|----------|-------------|
| Payments / inventory invariants | **Postgres** |
| Sessions / rate limits / cache | **Redis** |
| Flexible product attrs / aggregates | **Mongo** or Postgres JSONB |
| Huge write feeds / timelines | **Cassandra** |
| Friend-of-friend / fraud graph | **Neo4j** (or specialized) |
| Metrics | **Prometheus / TSDB** |
| Product text search | **Elasticsearch** (not “NoSQL vs SQL” alone) |

### “NoSQL” is not one thing

| Family | Optimize for |
|--------|--------------|
| KV | Get-by-key |
| Document | Document aggregates |
| Wide-column | Write scale + known queries |
| Graph | Multi-hop relationships |
| Time-series | Time-range metrics |

Postgres JSONB + extensions often cover “we thought we needed Mongo” cases.

## Why seniors get asked

The classic senior design fork. The winning answer is a matrix with trade-offs, not “NoSQL is web scale.”

## Simple example

```text
Orders + payments + inventory invariants → Postgres
Session tokens / rate limits             → Redis
Product catalog flexible attrs           → Mongo or Postgres JSONB
User activity feed at huge write QPS     → Cassandra
Friend-of-friend recommendations         → Neo4j (or specialized)
API latency metrics                      → Prometheus / TSDB
```

## When to use / when not / trade-offs

| Lean SQL when… | Lean NoSQL when… |
|----------------|------------------|
| Complex queries & integrity | Known keys, massive scale |
| Mature reporting on live OLTP (careful) | Specialized model (graph/time) |
| Team strength in relational | Access patterns fit the engine |

**Trade-offs:** SQL generality vs NoSQL scale/specialization; many systems are **polyglot** (Postgres + Redis + search).

## Common pitfalls

- Defaulting to Mongo for every new app  
- Ignoring operational complexity of clustered NoSQL  
- Using NoSQL then reinventing joins in app code poorly  
- Forgetting Postgres JSONB / extensions cover many “document” cases  

## Interview trigger phrase

> “I’d start from access patterns and transaction needs — Postgres by default, then Redis/Cassandra/Mongo where the pattern clearly wins.”

## Exercise

Pick stores for: payments ledger, product search, shopping cart, social follow-graph. One sentence justification each.
