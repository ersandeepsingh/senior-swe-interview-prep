# CAP Theorem

> In a distributed system, when the network **partitions**, you can keep **Consistency** or **Availability** — not both. Partition tolerance is not optional on the open internet.

## Plain English

Three letters:

| Letter | Meaning | User-facing feel |
|--------|---------|------------------|
| **C** Consistency | Every read sees the latest successful write | “My balance is always correct everywhere.” |
| **A** Availability | Every non-failing node answers (maybe stale) | “The app always responds.” |
| **P** Partition tolerance | System keeps working when nodes can’t talk | “A cable cut between DCs doesn’t kill us.” |

On a single machine, CAP barely matters. Across machines and regions, **partitions happen** (network blips, DC isolation). So the real choice is: **CP or AP**.

```text
                    ┌─────────────────┐
                    │  Network split  │
                    │  (Partition P)  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     ┌────────────────┐           ┌────────────────┐
     │   Choose CP    │           │   Choose AP    │
     │ Refuse some    │           │ Always answer  │
     │ requests until │           │ (may be stale  │
     │ quorum is safe │           │  or conflict)  │
     └────────────────┘           └────────────────┘
           Bank ledger                 Social likes
           Seat inventory              Product catalog browse
```

## Simple example

Two data centers hold your bank balance = ₹1000.

```text
        DC-A                         DC-B
     balance=1000                 balance=1000
           │                           │
           │     ✕ network cut ✕       │
           │                           │
     User withdraws ₹800          User reads balance
```

| Choice | What happens |
|--------|----------------|
| **CP** | DC-B refuses the read (or waits). You never show ₹1000 after ₹800 left. Safer money. |
| **AP** | DC-B still returns ₹1000. App “works,” but you can overspend until DCs reconnect and reconcile. |

**Same story, social likes:** AP is fine — a like count being off by 1 for a few seconds is acceptable. **Ticket booking seats:** CP (or careful locking) — two users must not get the same seat.

## Why prefer one over the other

| Prefer **CP** when… | Prefer **AP** when… |
|---------------------|---------------------|
| Wrong answer costs money/legal risk | Stale answer is annoying but OK |
| Inventory, payments, seats, ledger | Feeds, likes, views, recommendations |
| You’d rather return 503 than wrong data | You’d rather return *something* than error |

**Not “CP is more correct.”** It’s “wrong data is worse than downtime” vs the opposite.

### Real systems (interview name-drops)

- **CP-ish:** ZooKeeper, etcd, traditional single-primary Postgres with sync replicas that block on partition.
- **AP-ish:** DynamoDB (tunable), Cassandra (tunable), DNS, CDN caches, many shopping “browse” paths.

Most production systems are **not pure** CAP extremes — they pick per *use case* (checkout CP, product page AP).

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| CP under partition | Correctness | Some users get errors / higher latency waiting for quorum |
| AP under partition | Continuity of service | Temporary inconsistency; need conflict resolution later |
| Ignoring P | Simpler mental model | Reality breaks you — partitions *will* happen |

**Common interview trap:** Saying “we want all three.” Seniors say: *“Under partition we choose AP for the feed and CP for payments.”*

## Interview trigger phrase

> “Under a network partition I’d choose **CP** for money/inventory and **AP** for the social feed — wrong money is worse than a stale like count.”

## Exercise

**Design a ride-hailing “driver location” vs “trip payment” path.**

1. For **live map of nearby drivers**, argue AP or CP under a partition between regions — and why.
2. For **charging the rider’s card at trip end**, argue the other (or same) choice — and why.
3. Say one sentence you’d tell the interviewer about what the user sees when the link between Mumbai and Bangalore DCs is cut.
