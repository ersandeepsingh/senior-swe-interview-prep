# 07 · Distributed Systems — Foundational Theorems & Trade-offs

> The laws of physics for systems that span multiple machines.

---

## CAP theorem

**Definition:** In the presence of a network **P**artition, a distributed system can guarantee either **C**onsistency or **A**vailability, but not both.

**Simple explanation:** Partitions (network splits) *will* happen, so you don't really "choose" P — you choose what to do *during* one. **CP:** refuse requests that can't be made consistent (stay correct, sacrifice uptime). **AP:** keep serving, possibly returning stale data (stay up, sacrifice consistency). When there's no partition, you can have both.

**Example:** Two data centers lose their link.
- **CP system (e.g., a bank ledger):** rejects writes it can't confirm everywhere — you'd rather show an error than double-spend.
- **AP system (e.g., a shopping cart / DNS):** keeps accepting writes on each side and reconciles later — a briefly stale cart is fine.

---

## PACELC

**Definition:** An extension of CAP: if **P**artition, choose **A**vailability or **C**onsistency; **E**lse (normal operation), choose **L**atency or **C**onsistency.

**Simple explanation:** CAP only talks about the partition case. PACELC adds the everyday case: even with a healthy network, enforcing strong consistency (waiting for replicas to agree) costs latency. So you're always trading something.

**Example:**
- DynamoDB/Cassandra: **PA/EL** — favor availability during partitions and low latency normally (eventual consistency).
- Google Spanner: **PC/EC** — favor consistency always, accepting higher latency (uses synchronized clocks + consensus).

---

## Consistency spectrum

**Definition:** The range of guarantees about when and how writes become visible: strong, sequential, causal, read-your-writes, monotonic reads, eventual.

**Simple explanation:** "Consistency" isn't binary. **Strong** = everyone always sees the latest write (like a single machine). **Eventual** = replicas converge *eventually* if writes stop. In between are useful practical guarantees like **read-your-writes** (you always see your own updates) and **causal** (effects never appear before their causes).

**Example:**
- **Strong:** you post a comment; every reader worldwide sees it immediately (costly).
- **Read-your-writes:** you see your own comment instantly; others may see it a second later (good UX, cheaper).
- **Eventual:** your comment shows up for everyone within seconds — fine for likes/counters.

---

## Latency vs throughput

**Definition:** **Latency** is how long one operation takes; **throughput** is how many operations complete per unit time.

**Simple explanation:** They're related but distinct — and often in tension. Batching improves throughput but adds latency (you wait to fill the batch). A single fast car (low latency) vs a wide highway moving many cars (high throughput). Also watch *tail latency* (p99): a system can have great average latency but painful tails.

**Example:** A payment API can process 10,000 req/s (throughput) while each request takes 50ms (latency). Adding batching might push throughput to 20,000 req/s but raise per-request latency to 120ms — good for a data pipeline, bad for a checkout button.

---

## FLP impossibility

**Definition:** In a fully asynchronous network where even one node may fail, no consensus algorithm can guarantee it always terminates (reaches agreement).

**Simple explanation:** You can't build a *perfect* consensus system that always succeeds in bounded time when the network has no timing guarantees and nodes can crash. Real systems dodge this by using timeouts and randomness (partial synchrony) to make failure to agree extremely unlikely rather than impossible.

**Example:** Raft and Paxos "work" in practice because they assume messages *usually* arrive within some time and use election timeouts — they sidestep FLP by giving up the guarantee of always terminating in a purely async model.

---

## Fallacies of distributed computing

**Definition:** A classic list of false assumptions engineers make: the network is reliable, latency is zero, bandwidth is infinite, the network is secure, topology doesn't change, there's one administrator, transport cost is zero, the network is homogeneous.

**Simple explanation:** Code that works on one machine often breaks across the network because these assumptions fail. Every remote call can be slow, fail, arrive twice, or arrive out of order. Designing distributed systems means planning for all of that — retries, timeouts, idempotency, encryption.

**Example:** A dev writes `result = remoteService.getData()` assuming it's instant and reliable. In production the call sometimes takes 5s, sometimes times out, sometimes succeeds but the response is lost. The fix: add timeouts, retries with backoff, and make the operation idempotent — because the network is *not* reliable.
