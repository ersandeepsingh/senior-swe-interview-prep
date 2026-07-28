# Service Boundaries & DDD

> Draw service lines around **business meaning**, not around tables or teams' org chart alone. DDD gives language: bounded contexts, aggregates, ubiquitous language.

## Plain English

Services should own a coherent piece of the business. Crossing a boundary needs an explicit translation (API/events), not a shared God model. Other services ask via API or consume events — **no reaching into another service's DB**.

```text
  Bad boundary:  “UserService” owns users, orders, payments, notifications
  Better:        Identity | Ordering | Payments | Fulfillment
                 (each with its own model of “customer”)
```

## Essentials (must-know for this topic)

### Key DDD terms

| Term | Meaning |
|------|---------|
| **Bounded context** | Boundary where a word has **one** meaning (“Order” in Checkout ≠ Warehouse) |
| **Ubiquitous language** | Shared vocabulary inside a context |
| **Aggregate** | Cluster of entities as one consistency unit with a **root** (e.g. `Order` owns `OrderLines`) |
| **Invariant** | Rule enforced **inside** the aggregate; outside → eventual consistency via messages |
| **Anti-corruption layer** | Translate foreign models at the boundary |

### Data ownership rule

| Do | Don't |
|----|-------|
| Service **owns its data** | Shared DB across services |
| Integrate via API / events | `SELECT` another service's tables |
| Duplicate read models if needed | One enterprise God schema |

### Boundary smells

| Smell | Why it hurts |
|-------|--------------|
| **Entity-service** (one service per table) | Chatty, no business cohesion |
| Split by technical layer only | Controllers vs “DB service” |
| God “UserService” | Owns everything |
| Too-fine services | 10 sync calls per click |

## Simple example

E-commerce:

| Context | Owns | Does not own |
|---------|------|--------------|
| Catalog | Product, price, description | Stock reservation |
| Ordering | Cart, Order, OrderLines | Card charges |
| Payments | PaymentIntent, Charge | Shipping status |
| Fulfillment | Shipment, tracking | Product marketing copy |

When Checkout needs stock: call Inventory API or react to `StockReserved` events — don't `SELECT` Inventory's tables.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Strict bounded contexts | Clear ownership, evolvable models | Some duplication of data/concepts |
| Shared kernel / shared DB | Less duplication short-term | Hard coupling forever |
| Large aggregates | Strong invariants | Contention, hard to scale writes |
| Tiny aggregates | Parallelism | Cross-aggregate consistency harder |

## Pitfalls

- **Entity-service anti-pattern** — one service per table (`OrderLineService`).
- **Copying the org chart blindly** (Conway) without revisiting domain language.
- **One enterprise data model** forced across all contexts.
- **Chatty boundaries** — too-fine services that need 10 sync calls per click.

## Interview trigger phrase

> “I'd split on **bounded contexts** with clear **aggregates** and **data ownership** — services integrate via APIs/events, never by sharing a database.”

## Exercise

In a ride-hailing app, is “Driver” the same concept in Matching, Payroll, and Support? Sketch two fields that differ per context and how you'd sync identity across them.
