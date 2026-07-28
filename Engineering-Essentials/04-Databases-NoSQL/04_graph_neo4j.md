# Graph (Neo4j)

> Store **nodes and relationships** as first-class citizens — great when the question is “how are these connected?”

## Plain English

Relational DBs can model graphs with join tables, but deep traversals (`friends of friends of friends`) get painful. Graph DBs optimize walking edges. Use them when **relationships are the product**, not for every CRUD app.

## Essentials (must-know for this topic)

### Building blocks

| Concept | Meaning |
|---------|---------|
| **Node** | Entity (`User`, `Device`, `Account`) — has labels + properties |
| **Relationship** | Directed edge (`FRIENDS_WITH`, `BOUGHT`) — can have properties |
| **Label** | Node type tag (`:User`) |
| **Property** | Key/value on node or rel |
| **Cypher** | Neo4j query language (`MATCH` patterns) |

### Graph vs SQL vs KV (when which)

| Need | Prefer |
|------|--------|
| Multi-hop / variable-length paths | **Graph** |
| Flat CRUD by id + ACID joins | **SQL** |
| Get-by-key micro-latency | **KV** |
| One-hop FK only | SQL is fine |

### Traversal vocabulary

| Pattern | Meaning |
|---------|---------|
| `(a)-[:REL]->(b)` | One hop |
| `(a)-[:REL*1..3]-(b)` | Variable-length path (bound it!) |
| Pattern matching | Find structures (fraud rings, shared devices) |

### Interview caution flags

| Do | Don’t |
|----|-------|
| Index lookup properties (`User.id`) | Unbounded `*` in production |
| Limit depth / result size | Put all OLTP data in Neo4j “because relationships” |
| Use graph for the connected subgraph | Expect warehouse-style aggregations |

## Why seniors get asked

Recommendations, fraud rings, permissions/org charts, and network analysis. Seniors know when a graph engine beats recursive SQL.

## Simple example

```cypher
CREATE (a:User {id:'7', name:'Ada'})
CREATE (b:User {id:'8', name:'Bob'})
CREATE (a)-[:FRIENDS_WITH {since:2020}]->(b);

MATCH (u:User {id:'7'})-[:FRIENDS_WITH*1..2]-(f:User)
RETURN DISTINCT f.name;
```

## When to use / when not / trade-offs

| Use graph when… | Prefer SQL/KV when… |
|-----------------|---------------------|
| Deep / variable-length traversals | Flat CRUD by id |
| Relationship is the product | Simple one-hop foreign keys |
| Pattern detection (fraud) | Heavy aggregations over facts |

**Trade-offs:** natural for connected data; ops/expertise less common; global graph sharding is hard; not ideal as the only OLTP store for everything.

## Common pitfalls

- Putting all company data in Neo4j “because relationships”
- Unbounded `*` traversals in production without limits
- Ignoring indexes on node lookup properties
- Expecting SQL-style reporting performance

## Interview trigger phrase

> “If the core query is multi-hop relationships, I’d use a graph DB; for tabular transactions I’d keep Postgres and maybe export a subgraph.”

## Exercise

Detect fraud: accounts sharing devices and shipping addresses. Sketch 3 node types + relationships and a Cypher-style pattern that flags clusters.
