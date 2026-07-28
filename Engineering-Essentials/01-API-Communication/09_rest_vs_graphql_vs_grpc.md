# REST vs GraphQL vs gRPC

> Three ways to expose APIs — pick by **client needs, network shape, and contract strictness**, not fashion.

## Plain English

They solve different pains: REST = universal & cacheable; GraphQL = flexible client shapes; gRPC = fast, strict internal calls. The senior answer is a decision matrix, not “always X.”

## Essentials (must-know for this topic)

### Side-by-side

| | **REST** | **GraphQL** | **gRPC** |
|--|----------|-------------|----------|
| Mental model | Resources + HTTP verbs | Typed graph; client picks fields | RPC methods + Protobuf |
| Typical transport | JSON over HTTP/1.1 or 2 | JSON POST to one endpoint | Binary over **HTTP/2** |
| Contract | OpenAPI / conventions | Schema (SDL) | `.proto` IDL + codegen |
| Caching | Excellent (GET/CDN) | Harder | App-level / mesh |
| Browser / public | First-class | Good (HTTP) | Needs gateway / gRPC-Web |
| Streaming | Limited (SSE etc.) | Subscriptions | First-class (4 RPC types) |
| Over/under-fetch | Common issue | Designed to avoid | Fixed message shapes |

### Decision cheat sheet

| Situation | Lean toward |
|-----------|-------------|
| Public API, CDN caching, curl-friendly | **REST** |
| Mobile/web with many screens & nested data | **GraphQL** (or BFF) |
| Internal microservice mesh, high QPS, streaming | **gRPC** |
| Partners who mandate OpenAPI | **REST** |
| One product, two clients needing different aggregates | **BFF** (± GraphQL) |

### One-line trade-offs

- **REST:** simple ops story; over/under-fetch risk  
- **GraphQL:** flexible queries; caching & N+1 harder  
- **gRPC:** performance & contracts; weaker browser/public ergonomics  

**Boundary rule:** public edge often REST/GraphQL; internal mesh often gRPC — mix on purpose, not by accident.

## Why seniors get asked

This is the classic senior “which and why.” The answer is almost never “always X” — it’s a decision matrix with trade-offs.

## Simple example

Same “get order with user name”:

```http
# REST — maybe 2 calls or a BFF aggregate
GET /orders/42
GET /users/7
```

```graphql
# GraphQL — one round trip, exact fields
{ order(id:"42") { status user { name } } }
```

```protobuf
# gRPC — typed unary call
rpc GetOrderWithUser(GetOrderRequest) returns (OrderWithUser);
```

## When to use / when not / trade-offs

| Situation | Lean toward |
|-----------|-------------|
| Public API, CDN caching, curl-friendly | REST |
| Mobile/web with many screens & nested data | GraphQL (or BFF) |
| Internal microservice mesh, streaming | gRPC |
| Browser-only, simple CRUD | REST |
| Partners who mandate OpenAPI/REST | REST |

**Trade-offs in one line each:**

- REST: simple ops story; over/under-fetch risk  
- GraphQL: flexible queries; caching & N+1 harder  
- gRPC: performance & contracts; weaker browser/public ergonomics  

## Common pitfalls

- Picking GraphQL because it’s “modern” for a 5-endpoint CRUD API
- Exposing gRPC directly to random third parties
- Mixing all three without a clear boundary (public vs internal)
- Ignoring team skills and tooling cost

## Interview trigger phrase

> “Public CRUD → REST; flexible product UI → GraphQL or BFF; internal high-QPS → gRPC — I’d draw the boundary and not mix without reason.”

## Exercise

You’re building: (1) a public payments API for merchants, (2) a React Native app with nested feeds, (3) fraud-scoring between two Java services. Assign REST / GraphQL / gRPC to each and justify in one sentence each.
