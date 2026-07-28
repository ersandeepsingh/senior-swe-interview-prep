# Consistency Models

> After a write, **when** do readers see it? Strong consistency says “immediately (under rules)”; eventual says “soon.”

## Plain English

Distributed data forces a choice: how stale can a read be? Seniors tune quorums, explain anomalies to product, and don’t confuse **durability** with **consistency**.

## Essentials (must-know for this topic)

### Models (vocab)

| Model | Meaning |
|-------|---------|
| **Strong / linearizable** | After successful write, any read sees it (single-copy feel) |
| **Eventual** | Replicas converge; reads may be briefly stale |
| **Read-your-writes** | You see your own updates |
| **Monotonic reads** | You never go backward in time |
| **Causal** | Cause-before-effect order preserved |

### Quorum math (Dynamo-style)

| Symbol | Meaning |
|--------|---------|
| **N** | Replica count |
| **W** | Write ack quorum |
| **R** | Read quorum |

**Rule:** `R + W > N` → read/write quorums overlap → strong-ish consistency **for that key**.

| Example (N=3) | Behavior |
|---------------|----------|
| W=2, R=2 | Sees latest (overlap) |
| W=2, R=1 | Faster reads; may miss latest |
| W=1, R=1 | Fast; weakest |

### CAP (practical interview version)

Under **network partition**, you lean:

| Lean | Behavior |
|------|----------|
| **CP** | Refuse/fail rather than serve wrong data |
| **AP** | Serve possibly stale; stay available |

(Real systems are nuanced; still expected vocabulary.)

### Durability ≠ consistency

| Term | Question it answers |
|------|---------------------|
| **Durability** | Survives crash after commit? |
| **Consistency** | Do readers agree / see latest? |

## Why seniors get asked

Distributed data interviews live here. Seniors tune R/W quorums and explain stale reads to product.

## Simple example

```text
N=3 replicas
W=2  write waits for 2 nodes
R=1  read from 1 → may miss latest if that replica lagged
R=2  read from 2 → intersects write quorum → sees latest (for that key)
```

```python
# App-level: after write, read from primary (read-your-writes)
db.primary.execute("UPDATE ...")
db.primary.execute("SELECT ...")  # not a lagging replica
```

## When to use / when not / trade-offs

| Stronger consistency when… | Eventual when… |
|----------------------------|----------------|
| Money, inventory, authz | Social likes, metrics, caches |
| Low multi-region conflict | Need multi-region low latency writes |

**Trade-offs:** strong → higher latency / lower availability under partition; eventual → faster/more available, anomalies & conflict resolution.

## Common pitfalls

- Saying “eventual consistency” without naming the anomaly you’ll accept  
- Reading from replicas after write and surprising users  
- Quorum math wrong (`R+W ≤ N`)  
- Confusing durability (survives crash) with consistency (readers agree)  

## Interview trigger phrase

> “I’d pick strong consistency for ledger-like data; for multi-region feeds I’d use eventual with quorum reads/writes and call out stale windows.”

## Exercise

Shopping cart in 3 AZs. Choose N/R/W for “checkout must see latest cart.” What latency do you pay? When would you accept R=1?
