# 10 · Distributed Systems — Consistency, Time & Ordering

> Agreeing on "what happened first" when there's no single clock.

---

## Logical clocks (Lamport timestamps)

**Definition:** A counter each node increments on every event and includes in messages, used to impose a consistent ordering of events without real time.

**Simple explanation:** You can't trust wall clocks across machines, but you can count. Each node keeps a counter, bumps it on every event, and when it receives a message it sets its counter to `max(local, received) + 1`. This guarantees that if event A *caused* B, then timestamp(A) < timestamp(B). It gives a total order but can't tell you if two events were truly concurrent.

**Example:** Node1 sends a message at Lamport time 5. Node2 (at time 3) receives it and jumps to `max(3,5)+1 = 6`. Now any event on Node2 after receiving is correctly ordered *after* Node1's send.

---

## Vector clocks

**Definition:** An array of counters (one per node) that captures causality and can detect *concurrent* (conflicting) updates.

**Simple explanation:** Lamport clocks can't tell "concurrent" from "ordered." Vector clocks can: each node tracks a counter for every node. By comparing two vectors you can tell if one happened-before the other or if they're concurrent (a conflict needing resolution).

**Example:** Two users edit the same shopping cart offline.
- Update X has vector `[A:2, B:0]`, update Y has `[A:1, B:1]`.
- Neither dominates the other → they're **concurrent** → the system flags a conflict to merge (e.g., union the carts) rather than silently overwriting.

---

## Physical clock issues

**Definition:** The problems caused by relying on wall-clock time across machines: clock skew, drift, and NTP corrections that can jump backward.

**Simple explanation:** Server clocks disagree by milliseconds-to-seconds and can even move backward when NTP syncs. So "latest timestamp wins" can pick the *wrong* write. Never assume two machines' clocks are comparable to sub-second precision. (Google Spanner solves this with atomic clocks + GPS and a "TrueTime" uncertainty window.)

**Example:** Two servers write to the same key. Server A's clock is 200ms fast, so its *older* write gets a *later* timestamp and wins under last-write-wins — silently discarding the genuinely newer write from Server B.

---

## Conflict resolution

**Definition:** Strategies for deciding the outcome when concurrent writes disagree: last-write-wins (LWW), CRDTs, or application-level merges.

**Simple explanation:** When two writes conflict, someone must decide the result. **LWW** is simple but loses data (one write silently discarded). **App-level merge** applies domain logic (e.g., keep the higher bid). **CRDTs** are data types mathematically designed to merge automatically without conflict.

**Example:**
- LWW: two profile-name edits → keep the one with the later timestamp (may lose the other).
- App merge: two edits to a shared doc → merge both paragraphs.
- Shopping cart: union the items so nothing a user added is lost.

---

## CRDTs (Conflict-free Replicated Data Types)

**Definition:** Data structures designed so that concurrent updates on different replicas always merge to the same correct result, automatically, without coordination.

**Simple explanation:** CRDTs bake conflict resolution into the data type itself using commutative/associative operations. Replicas can update independently and offline; when they sync, the merge is deterministic and order-independent. Great for collaborative editing and offline-first apps.

**Example:** A **G-Counter** (grow-only counter) keeps a per-node count; the value is the sum. Two nodes each increment independently offline; on sync you add their contributions — no lost updates, no conflict. Collaborative editors (like some Google-Docs-style tools) use sequence CRDTs so simultaneous typing merges cleanly.

---

## Idempotency

**Definition:** A property where performing an operation multiple times has the same effect as performing it once.

**Simple explanation:** Because networks lose responses, clients retry — and a retry might mean the same request runs twice. Idempotency ensures the duplicate is harmless. You typically attach an **idempotency key**; the server records it and, on a repeat, returns the original result instead of doing the work again.

**Example:** A payment request carries `Idempotency-Key: order-991`. The client times out and retries. The server sees it already processed `order-991`, so it returns the original success response instead of charging the card a second time.

---

## Exactly-once vs at-least-once vs at-most-once

**Definition:** The three message-delivery guarantees.
- **At-most-once:** may lose messages, never duplicates.
- **At-least-once:** never loses, may duplicate.
- **Exactly-once:** each message effectively processed once.

**Simple explanation:** True end-to-end "exactly-once" delivery is essentially impossible over an unreliable network. What systems actually do is **at-least-once delivery + idempotent processing**, which gives *effectively-once* results. If someone claims "exactly-once," ask how — it's almost always at-least-once plus dedup.

**Example:** Kafka delivers a payment event at-least-once, so the consumer might see it twice. The consumer dedupes on `payment_id` (idempotent processing) so the customer is charged once. That combination is what people *mean* by "exactly-once."
