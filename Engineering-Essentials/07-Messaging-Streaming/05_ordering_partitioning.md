# Ordering & Partitioning

> Total global order is expensive and rarely needed. Systems usually guarantee **order per key** (orderId, userId) by sending that key to **one partition / one FIFO group**.

## Plain English

| Guarantee | Meaning |
|-----------|---------|
| **No order** | Standard SQS / multi-queue chaos — fine for independent jobs |
| **Per-partition / per-key order** | All records with same key go to same partition; that log is FIFO |
| **Global order** | Single partition or single queue — throughput ceiling |

```text
  key(orderId) ──hash──► partition
  order-7 events: Created → Paid → Shipped   ✓ in order on that partition
  order-7 vs order-9: no order between them   ✓ usually fine
```

Kafka: order **inside a partition** only. Consumers must process a partition **sequentially** (or you break order).

## Essentials (must-know for this topic)

### Ordering guarantees compared

| Guarantee | How you get it | Throughput |
|-----------|----------------|------------|
| **None / best-effort** | Standard SQS, multi-worker chaos | Highest |
| **Per-key / per-partition** | Same key → same Kafka partition or SQS FIFO `MessageGroupId` | Scales with distinct keys |
| **Global** | Single partition / single queue | Bottleneck |

### Partitioning rules of thumb

| Rule | Why |
|------|-----|
| Pick key = entity whose transitions must be ordered (`orderId`, `sku`) | State machines stay correct |
| Don’t need order between different keys | Enable parallelism |
| Hot key → hot partition | Celebrity traffic pins one shard |
| Parallelize **inside** a partition | Breaks order |

**Kafka reminder:** topic-wide order is a myth. SQS FIFO: order per `MessageGroupId`, not across groups.

## Simple example

**Inventory for SKU `widget-1`:**

```text
  Bad: random partitions
    reserve +10 and reserve -1 arrive reordered → wrong stock

  Good: key = sku
    all widget-1 mutations on one partition → serial apply
```

**SQS FIFO:** `MessageGroupId = orderId` → order preserved per group; different groups in parallel.

## When to use / trade-offs

| Prefer **per-key order** when… | Prefer **unordered** when… |
|--------------------------------|----------------------------|
| State machine / balance / inventory | Embarrassingly parallel jobs |
| Event sourcing per aggregate | Throughput matters more than order |

| Prefer **more partitions** when… | Prefer **fewer** when… |
|----------------------------------|------------------------|
| Need consumer parallelism | Need wider ordering scope |
| High throughput | Simpler ops; hot keys less split |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Single partition global order | Simple mental model | Throughput bottleneck |
| Keyed partitions | Parallelism + local order | Hot keys overload one partition |
| Parallel consume inside partition | Speed | Broken order |

## Pitfalls

- Assuming Kafka gives **topic-wide** order.  
- Rebalancing / errors causing **out-of-order** handling if you parallelize carelessly.  
- Hot key (`userId=celebrity`) pins one partition.  
- Changing partition count remaps keys → temporary order weirdness across old/new.  
- FIFO everywhere “for safety” → unnecessary throughput hit.

## Interview trigger phrase

> “I’d choose a **partition key** so all events for one entity stay ordered — **per-key order**, not global — and scale by adding partitions for different keys.”

## Exercise

**Bank ledger + notification emails.**

1. What partition key for ledger entries? For email-send jobs?  
2. Why might email be unordered while ledger must be ordered?  
3. One user is 20% of writes — what happens to their partition, and name one mitigation.
