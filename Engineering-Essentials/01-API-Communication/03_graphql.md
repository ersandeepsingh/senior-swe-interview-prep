# GraphQL

> One endpoint; the client asks for exactly the fields it needs via a typed schema — queries, mutations, and optional subscriptions.

## Plain English

Instead of many REST URLs that each return a fixed JSON shape, GraphQL exposes a **schema** (types + fields). The client writes a query that looks like the JSON it wants. The server runs **resolvers** per field.

## Essentials (must-know for this topic)

### Operation types

| Operation | Purpose | Side effects? |
|-----------|---------|---------------|
| **Query** | Read data | No (by convention) |
| **Mutation** | Write / change state | Yes |
| **Subscription** | Long-lived stream of events | Listen only (updates pushed) |

Typically one HTTP endpoint (`POST /graphql`); subscriptions often use WebSockets.

### Schema building blocks

| Concept | Meaning |
|---------|---------|
| **Type** | Object shape (`Order { id status user }`) |
| **Field** | Property on a type; may take arguments |
| **Schema** | Root `Query` / `Mutation` / `Subscription` + all types |
| **Resolver** | Function that returns a field’s value (often one per field) |
| **Scalar** | Leaf values: `String`, `Int`, `ID`, custom (`DateTime`) |

### N+1 + DataLoader (one-liner interview pair)

Resolving `orders { user { name } }` can fire **one user query per order**. **DataLoader** (or equivalent batching) collects keys in one tick and loads users in **one** `WHERE id IN (…)`.

### GraphQL vs REST (this topic’s angle)

| | GraphQL | REST |
|--|---------|------|
| Shape | Client picks fields | Server fixes representation |
| Endpoints | Usually one | Many resource URLs |
| Caching | Harder (POST body) | Natural GET + CDN |
| Over/under-fetch | Solved by design | Common pain |

Also know: **query depth/cost limits**, persisted queries, and that mutations still need **idempotency** when clients retry.

## Why seniors get asked

Mobile and BFF teams love GraphQL for flexible UIs. Interviewers probe whether you understand the cost: complex resolvers, caching difficulty, and N+1.

## Simple example

```graphql
# Schema sketch
type Order {
  id: ID!
  status: String!
  user: User!
}
type Query {
  order(id: ID!): Order
}
```

```graphql
query {
  order(id: "42") {
    status
    user { name email }
  }
}
```

```http
POST /graphql
Content-Type: application/json

{"query":"query { order(id:\"42\") { status user { name } } }"}
```

## When to use / when not / trade-offs

| Use GraphQL when… | Prefer REST/gRPC when… |
|-------------------|------------------------|
| Many clients need different shapes of the same graph | Simple CRUD, CDN caching of GETs |
| Frontend iterates fast on fields | Internal high-QPS binary RPCs |
| You invest in schema governance | Public third parties that expect REST |

**Trade-offs:** great for under/over-fetching; harder HTTP caching; one “fat” endpoint needs auth, complexity limits, and query cost analysis.

## Common pitfalls

- Unbounded nested queries that DOS the DB
- Ignoring N+1 until production melts
- Treating mutations like fire-and-forget without idempotency
- Exposing internal DB models 1:1 as the public schema

## Interview trigger phrase

> “GraphQL fits when clients need flexible graphs of data — I’d enforce query depth/cost limits and use DataLoader to kill N+1.”

## Exercise

Sketch a GraphQL query for “order 42 with line items and each product’s name.” Then explain in one sentence how DataLoader would batch product loads.
