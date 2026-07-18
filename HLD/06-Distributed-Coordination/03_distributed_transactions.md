# Distributed Transactions

> One business action touches **many services**. You can’t open one ACID transaction across them — so you pick **2PC**, **Saga**, or **TCC**, and accept compensating reality.

## Plain English

Microservices each own a DB. “Place order” may touch inventory, payment, and shipping. A single `BEGIN/COMMIT` across those DBs doesn’t exist in practice (XA is rare and painful).

| Pattern | How it works | Feel |
|---------|--------------|------|
| **2PC** | Coordinator: prepare all → commit all (or abort) | Strong; blocking; coordinator risk |
| **Saga** | Sequence of local txns + **compensations** on failure | Eventual; no global lock |
| **TCC** | Try (reserve) → Confirm / Cancel | Explicit reservation; good for money |

```text
  2PC:                    Saga:                   TCC:
  Coord                   Order → Pay → Ship      Try reserve seat+pay
    │ prepare               │ fail Pay              │
    ├─ DB1 OK               ▼                       ▼
    ├─ DB2 OK             Compensate Order        Confirm both
    ▼ commit all          (cancel order)          or Cancel both
```

## Simple example

Book flight + hotel + charge card.

**2PC:** flight DB, hotel DB, payment prepare holds locks until commit — if coordinator dies mid-flight, resources stay locked (**blocking**).

**Saga (choreography or orchestration):**

```text
  1. CreateOrder (pending)
  2. ReserveInventory
  3. ChargePayment   ← fails
  4. Compensate: ReleaseInventory, CancelOrder
```

User may briefly see “pending.” **Orchestrator** (workflow engine) is easier to reason about than pure event choreography at interview depth.

**TCC:** Try: hold seat + auth hold on card. Confirm: finalize. Cancel: release seat + void hold. Nothing “half booked” after cancel.

## Why prefer one over the other

| Prefer **2PC** when… | Prefer **Saga** when… | Prefer **TCC** when… |
|----------------------|-----------------------|----------------------|
| Same org, XA-capable DBs, short txns | Long-running, many microservices | Need explicit reserve/confirm (tickets, wallets) |
| Strong atomicity worth blocking | Compensations are designable | Try must be reversible cleanly |
| Rare cross-DB paths | High availability under partial failure | Payment + inventory co-design |

**Why not always 2PC?** Coordinator SPOF, locks, poor fit for HTTP microservices and polyglot stores. **Why not always Saga?** Compensations are hard (refund ≠ undo); visibility of intermediate states. **Idempotent steps** are mandatory in Saga/TCC.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| 2PC | Atomic all-or-nothing | Availability, latency, ops pain |
| Saga | Loose coupling, scales | Eventual consistency; complex undo |
| TCC | Clear reserve semantics | More API surface; Try must not overcommit |
| Outbox + events | Reliable handoff between services | At-least-once; need idempotency |

**Trap:** “We’ll use distributed transactions” without naming failure + compensation. Seniors pick **Saga/TCC** for service boundaries and **local ACID** inside each service.

**Orchestration tip:** Temporal / Step Functions / custom orchestrator keeps the Saga graph visible; choreography (pure events) is harder to debug in a 45-min design.

**Outbox pattern:** commit business row + outbox event in one local txn, then publish — avoids “DB committed but Kafka never got the message.”

## Interview trigger phrase

> “Across services I’d use a **Saga or TCC** with compensations — 2PC only if we’re on XA and can tolerate blocking; each service stays locally transactional.”

## Exercise

**Design checkout: inventory + payment + shipment.**

1. Sketch a happy-path Saga and the compensate steps if payment fails after inventory reserve.
2. Why might TCC beat Saga for “hold inventory 10 minutes”?
3. One sentence on what the UI shows while the Saga is mid-flight.
