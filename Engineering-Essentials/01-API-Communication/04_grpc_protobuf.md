# gRPC / Protobuf

> Binary RPC over HTTP/2: you define contracts in an IDL (Protobuf), generate stubs, and call methods like local functions — with optional streaming.

## Plain English

**Protobuf** is a compact binary schema. You write a `.proto` file; both sides generate code. **gRPC** uses that schema to call `GetOrder(id)` across the network. Unlike REST’s resource URLs, gRPC is **RPC-shaped**: named methods on a service.

## Essentials (must-know for this topic)

### RPC types (unary vs streaming)

| Type | Signature shape | Use when |
|------|-----------------|----------|
| **Unary** | `req → resp` | Normal request/response |
| **Server streaming** | `req → stream resp` | Server pushes many messages (watch, feed) |
| **Client streaming** | `stream req → resp` | Client uploads many; one summary back |
| **Bidirectional** | `stream ↔ stream` | Chat, interactive duplex |

### Protobuf’s role

| Piece | Why it matters |
|-------|----------------|
| **`.proto` IDL** | Single source of truth for types + RPCs |
| **Field numbers** | Wire identity — **never reuse** after release |
| **Codegen** | Stubs/clients in many languages |
| **Binary encoding** | Smaller/faster than JSON for internal RPC |
| **Evolution** | Add optional fields; don’t change types/numbers |

### Why HTTP/2

| HTTP/2 feature | gRPC benefit |
|----------------|--------------|
| **Multiplexing** | Many RPCs on one connection |
| **Binary framing** | Efficient streaming |
| **Header compression** | Less overhead on chatty calls |

Browsers don’t speak gRPC natively → **gRPC-Web** or a gateway for public/web clients.

### Deadlines & errors (quick)

Always set **timeouts/deadlines** on calls. Status codes are gRPC statuses (`OK`, `NOT_FOUND`, `UNAVAILABLE`, …), mapped at gateways when exposing HTTP.

## Why seniors get asked

Internal microservice communication often moves from JSON REST to gRPC for speed and strict contracts. Seniors must know when binary RPC beats REST — and when browser/public API constraints say no.

## Simple example

```protobuf
syntax = "proto3";
service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc WatchStatus (WatchRequest) returns (stream OrderStatus); // server streaming
}
message GetOrderRequest { string id = 1; }
message Order { string id = 1; string status = 2; int64 total_cents = 3; }
```

Client pseudocode:

```python
stub = OrderServiceStub(channel)
order = stub.GetOrder(GetOrderRequest(id="42"), timeout=2.0)
```

## When to use / when not / trade-offs

| Use gRPC when… | Prefer REST/JSON when… |
|----------------|------------------------|
| Service-to-service, typed contracts | Public browser APIs, easy curl/debug |
| Low latency, high QPS, streaming | Partners who only speak REST |
| Polyglot teams with codegen | Quick scripts and ad-hoc exploration |

**Trade-offs:** smaller payloads + strong typing vs harder debugging, limited browser support (need gRPC-Web/proxy), schema evolution discipline required.

## Common pitfalls

- Breaking wire compatibility (reusing field numbers, changing types)
- No deadlines/timeouts on every call
- Using gRPC for public mobile APIs without a gateway
- Ignoring load-balancer / HTTP/2 support in the mesh

## Interview trigger phrase

> “For internal services I’d use gRPC + Protobuf for typed, multiplexed calls; for public HTTP clients I’d keep REST or put a gateway in front.”

## Exercise

List one unary and one streaming RPC for a chat backend. Name one Protobuf evolution rule you’d follow so old clients keep working.
