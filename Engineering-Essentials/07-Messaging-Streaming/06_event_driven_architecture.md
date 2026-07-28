# Event-Driven Architecture

> Services communicate by emitting and reacting to **events** instead of (or in addition to) synchronous request chains. Related ideas: **choreography vs orchestration**, **event sourcing**, and **CQRS**.

## Plain English

| Style | Who drives the workflow? |
|-------|--------------------------|
| **Choreography** | Each service listens and reacts; no central conductor |
| **Orchestration** | A workflow engine / orchestrator tells steps what to do |

| Pattern | Idea |
|---------|------|
| **Event sourcing** | Store facts as an append-only event log; state = fold(events) |
| **CQRS** | Separate write model from read model(s) |

```text
  Choreography:                Orchestration:
  OrderPlaced                  Orchestrator
    → Inventory reserves         → call Inventory
    → Payment charges            → call Payment
    → Email sends                → call Email
```

## Essentials (must-know for this topic)

### Choreography vs orchestration

| | **Choreography** | **Orchestration** |
|---|------------------|-------------------|
| Driver | Services react to events | Central workflow / saga orchestrator |
| Coupling | Loose; hard to see full flow | Explicit steps; clearer ownership |
| Best for | Simple fan-out reactions | Long flows, timeouts, compensations |

### Related patterns (definitions)

| Pattern | Meaning |
|---------|---------|
| **Domain event** | Fact that already happened (`OrderPlaced`) |
| **Saga** | Multi-step workflow with **compensations** on failure |
| **CQRS** | Separate write model from read model(s) |
| **Event sourcing** | Persist append-only events; state = fold(events) |
| **Outbox** | Reliably emit events after DB commit |

**Not the same:** “we publish after SQL update” ≠ full event sourcing. Use ES/CQRS when audit / multiple read models justify complexity.

## Simple example

**Order flow (choreography):**

```text
  Checkout publishes OrderPlaced
  Inventory: reserve → publishes InventoryReserved (or Rejected)
  Payment: listens InventoryReserved → charge → PaymentCaptured
  Shipping: listens PaymentCaptured → create shipment
```

**CQRS:** writes go to order service; a projector builds a `order_search` read DB / Elasticsearch from events.

**Event sourcing:** account balance isn’t a mutable row alone — it’s the sum of `Deposited` / `Withdrawn` events (with snapshots for speed).

## When to use / trade-offs

| Prefer **choreography** when… | Prefer **orchestration** when… |
|-------------------------------|--------------------------------|
| Simple reactions, few steps | Long workflows, compensations, visibility |
| Teams own their reactions | Need timeouts, human tasks, audit of process |

| Prefer **event sourcing** when… | Prefer **CRUD state** when… |
|---------------------------------|------------------------------|
| Audit, time travel, complex domain | Simple entities; team unfamiliar with ES |
| Many derived read models | One primary read/write model is enough |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Event-driven | Decoupling, scale, resilience | Debugging harder; eventual consistency |
| CQRS | Tailored reads | Sync lag; more moving parts |
| Event sourcing | Perfect audit trail | Schema evolution, replay ops skill |

## Pitfalls

- **Distributed monolith**: events that are really RPC in disguise (request/response over topics).  
- No schema versioning → poison consumers on field rename.  
- Choreography spaghetti with cyclic events.  
- Dual writes without outbox.  
- Claiming event sourcing when you only have “we publish after SQL update.”

## Interview trigger phrase

> “I’d use **events for fan-out and decoupling**, **orchestration when the workflow needs a single owner**, and I’d only take **event sourcing/CQRS** where audit or multiple read models justify the complexity.”

## Exercise

**Food delivery: place order → restaurant accept → courier assign → deliver.**

1. Sketch choreography vs orchestration for this flow (3–5 bullets each).  
2. Where would a saga compensation run if payment fails after reserve?  
3. Is event sourcing required here? Defend yes or no in two sentences.
