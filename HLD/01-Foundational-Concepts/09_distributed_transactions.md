# Distributed Transactions, 2PC, and SAGA

Distributed transactions coordinate operations across multiple databases, services, or systems, so that several changes either all happen (“commit”) or none do (“abort/rollback”). They’re critical where business correctness demands atomicity, but are hard due to failures, network partitions, and the distributed nature of systems.

---

## Why Distributed Transactions are Hard

- **Partial failure:** Some services might succeed, others might fail.
- **Network unreliability:** Messages can be delayed or lost, nodes can crash.
- **Atomicity vs Availability:** Achieving perfect atomicity (ACID) can block or slow down the overall system—CAP theorem rears its head.

---

## 2-Phase Commit (2PC)

2PC is a classic protocol for atomic distributed transactions. It involves a _coordinator_ and multiple _participants_ (databases/services).

### How 2PC Works

1. **Prepare (Voting) Phase**
   - Coordinator asks all participants if they can commit (“prepare to commit?”).
   - Each prepares changes _locally_ and replies “yes” (ready) or “no” (cannot commit).
2. **Commit (Decision) Phase**
   - If all reply “yes,” coordinator sends “commit” to all; otherwise, sends “abort/rollback.”
   - Each participant either finalizes or rolls back accordingly.

```
Coordinator          DB1            DB2

   |---prepare--->|         |           |
   |<--ready?-----|         |           |
   |              |---prepare--->|      |
   |              |<--ready?-----|      |
   |---commit/abort-->|------->|        |
```

**Pros:** Strong all-or-nothing guarantee.

**Cons:**  
- **Blocking:** If coordinator fails at the wrong time, participants can be stuck.
- **Performance:** Slower, cannot handle large numbers of participants well.
- **Partition sensitivity:** Not tolerant to network splits.

### Real-World Example

**Bank Transfer Across 2 Banks**
- Alice transfers \$100 from Bank A (her account) to Bank B (Bob’s account).
- Both banks must agree to commit (A debits, B credits). With 2PC:
  1. Coordinator says “prepare.”  
  2. Both banks lock funds and reply “ready.”  
  3. Coordinator says “commit.”  
  4. If one fails, coordinator says “rollback.”  

---

## SAGA Pattern

A SAGA breaks a big distributed transaction into smaller, local transactions, each of which can be _compensated_ (undone) if something later in the chain fails.

### How SAGA Works

- **Choreography:** Each service performs its part and publishes events, triggering the next service.
- **Orchestration:** A central orchestrator calls each service in order.

Each step is committed immediately. If something fails in a later step, previous steps are compensated with “undo” actions.

**Pros:**  
- **Non-blocking, scalable**—no global locks, suitable for microservices.
- **Eventual consistency:** Each step can finish independently, but system as a whole may be “inconsistent” temporarily.

**Cons:**  
- Compensation may be partial or hard (cannot always “undo” real-world effects).
- Visible intermediate states (real-world consequences must be acceptable).

### Real-World Example

**E-commerce Order Processing**

1. **Reserve item in inventory**
2. **Charge customer’s credit card**
3. **Create shipping order**

If step 3 (create shipping order) fails:
- Compensate step 2: refund the credit card.
- Compensate step 1: release the inventory.

---

## Other Concepts and Strategies

### 3-Phase Commit (3PC)

An improvement over 2PC designed to reduce blocking by adding an extra step. It tries to ensure participants can safely decide to commit/abort even if coordinator fails—but is rarely used in practice due to complexity and still imperfect in real networks.

### Idempotency

Making operations repeatable (idempotent) helps ensure correctness: if a failure leads to retry, the system won’t double-charge or double-update.

### Outbox Pattern

De-couple changes and messaging: write transaction + “outbox” message atomically, then asynchronously push messages/events to other services.

---

## Example Code

### 2PC (Pseudo-Python)
```python
# Simplified 2PC infrastructure
coordinator.prepare([db1, db2])
# Both reply 'ready'
coordinator.commit()  # or abort() if any fail
```

### SAGA (Pseudo-workflow)
```python
# Orchestration pattern
try:
    reserve_inventory(order)
    charge_card(order)
    create_shipment(order)
except ShipmentException:
    refund_card(order)
    release_inventory(order)
```

---

## In Summary

- Use **2PC** for small, critical, strongly consistent operations—trade off availability and speed.
- Use **SAGA** for business processes across microservices when you can accept eventual consistency and can design compensating actions.

**Interview tip:**  
_“In a microservice system, I’d prefer SAGA patterns for distributed long-running operations, using event choreography or orchestration. Only for short, highly critical, fully reversible business operations would I consider classic 2PC, and even then, only if I can accept the blocking and performance tradeoffs.”_

---