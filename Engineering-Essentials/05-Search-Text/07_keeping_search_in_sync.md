# Keeping Search in Sync

> Your DB is source of truth; the search index is a **derived view**. You must keep them aligned via dual writes, CDC, or rebuilds — accepting **lag** and designing for **idempotent** updates.

## Plain English

When Postgres changes, Elasticsearch must follow. Search designs fail on **sync**, not on query DSL. Pick a strategy that survives partial failure, and have a reindex playbook for mapping changes.

## Essentials (must-know for this topic)

### Strategies compared

| Strategy | How | Risk / lag |
|----------|-----|------------|
| **Dual write** | App writes DB + ES | One succeeds → **drift**; low lag if both OK |
| **Outbox** | DB txn + outbox row → async indexer | Brief lag; strong correctness |
| **CDC** (Debezium/Kafka) | Stream DB changes → indexer | Lag; ops complexity |
| **Periodic reindex** | Batch from DB | Simple; longer lag |
| **Change streams** | Mongo-style stream | Similar to CDC |

### Must-design-for

| Concern | Approach |
|---------|----------|
| **Idempotency** | Upsert by doc id; dedupe on event id |
| **Deletes** | Explicit delete events — easy to forget |
| **Ordering** | Per-id ordering or version/seq checks |
| **Lag** | Product accepts seconds; don’t promise sync read-after-write unless you read DB |
| **Repair** | Reconciliation job / partial reindex |

### Reindex without downtime

| Step | Action |
|------|--------|
| 1 | Build `products_v2` from DB (new mappings) |
| 2 | Dual-write or catch-up CDC into v2 |
| 3 | **Alias swap** `products` → `products_v2` |
| 4 | Drop old index |

Never “change mappings in place” on a live incompatible field.

### Failure vignette (interview)

ES down 5 minutes: outbox/CDC **queues** events; indexer drains when ES returns; dual-write without queue **loses** updates unless you reconcile.

## Why seniors get asked

Search designs fail on sync, not on query DSL. Seniors own consistency lag and rebuild playbooks.

## Simple example

```text
OrderService:
  1. BEGIN; UPDATE products ...; INSERT outbox_event; COMMIT;
  2. Publisher reads outbox → Kafka topic product-updates
  3. Indexer consumes → ES index/update/delete by product id
  4. Mark outbox processed (idempotent on event id)
```

```bash
# Reindex with zero downtime (alias swap)
# index products_v2 ← reindex from DB
# alias products → products_v2
```

Pseudocode indexer:

```python
def on_product_event(e):
    if e.type == "deleted":
        es.delete(index="products", id=e.id)
    else:
        doc = load_from_db(e.id)  # or use payload
        es.index(index="products", id=e.id, document=doc, version=e.version)
```

## When to use / when not / trade-offs

| Prefer CDC/outbox when… | Dual write when… |
|-------------------------|------------------|
| You care about correctness under failures | Prototypes / low stakes |
| Multiple consumers need the same change stream | Tiny apps |

**Trade-offs:** sync lag (seconds) vs transactional perfection; rebuilds cost CPU/time; dual write is a consistency footgun.

## Common pitfalls

- Dual write without reconciliation jobs  
- Not handling deletes  
- Reindexing by changing mappings in place (breaks)  
- Assuming ES update is synchronous with the API response  

## Interview trigger phrase

> “Postgres is source of truth; I’d publish via outbox/CDC to Elasticsearch idempotently, accept brief lag, and reindex with alias swap for mapping changes.”

## Exercise

Product price updates must appear in search within ~2s. Pick dual-write vs outbox and explain failure handling when ES is down for 5 minutes. How do you repair drift?
