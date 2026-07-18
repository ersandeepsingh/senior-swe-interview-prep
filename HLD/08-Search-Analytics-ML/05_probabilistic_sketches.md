# Probabilistic Sketches

> Exact distinct counts and set membership over huge streams are expensive. **Sketches** trade a little accuracy for tiny memory: **Bloom filters**, **HyperLogLog**, **Count-Min** — know when “approximately” is enough.

## Plain English

When cardinality is billions, storing every key is impossible. Sketches keep a **small summary** with known error bounds.

| Sketch | Answers | Error mode |
|--------|---------|------------|
| **Bloom filter** | “Might be in set?” / definitely not | False positives; no false negatives (standard Bloom) |
| **HyperLogLog (HLL)** | Approx distinct count (cardinality) | ± few % typical |
| **Count-Min Sketch** | Approx frequency / heavy hitters | Over-estimate counts |

```text
  Stream of user_ids ──► HLL ──► ~distinct DAU (KB not GB)

  URL seen before? ──► Bloom ──► "no" = sure skip
                                 "yes" = maybe; check DB

  Top search terms ──► Count-Min ──► rough frequencies
```

## Simple example

**CDN / cache:** Bloom of cached keys — avoid hitting origin on definite misses (or Bloom of “exists in DB” for negative caching). **Analytics:** HLL for unique visitors per day across Kafka partitions (HLLs are **mergeable**). **Rate abuse:** Count-Min for approximate hit counts per IP without storing every key.

```text
  Notification dedup:
    Bloom "already sent?" 
      no  → send + add
      yes → check exact store (or skip if soft-ok)
```

Redis has native Bloom / HLL / CMS — name-drop friendly. Guava Bloom, stream-lib, etc. in app code.

## Why prefer one over the other

| Prefer **sketch** when… | Prefer **exact** when… |
|-------------------------|------------------------|
| Huge cardinality / streams | Money, entitlements, exact billing |
| Merge across shards needed | Legal “must be precise” counts |
| Memory bound | Set is small; RAM OK |

**Bloom for passwords?** No — wrong tool. Bloom for “have we seen this event id?” to cheap-reject duplicates before DB — yes, with care about false positives.

**Counting Bloom / Cuckoo** variants if you need deletes — mention only if asked.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Bloom | Tiny membership tests | False positives; deletes hard (unless counting Bloom) |
| HLL | Tiny distinct counts | Approx only; not “who” |
| Count-Min | Tiny freq estimates | Overcounts; need config for error |
| Exact HyperLogLog++ params | Tunable accuracy | Slightly more memory |

**Trap:** Using HLL where you need the actual set of IDs. Sketches answer **aggregates / maybe-membership**, not retrieval of members. Also: don’t bill customers from Count-Min alone.

**Sizing intuition:** Bloom ~ few bits per element at chosen false-positive rate; HLL often ~KB for huge distinct counts — contrast with “store every user_id in Redis.”

**Mergeability:** HLLs and Count-Min merge across shards; perfect for Kafka partition-local aggregation then roll-up.

## Interview trigger phrase

> “For DAU I’d use **HLL**, for cheap negative lookups a **Bloom filter**, and **Count-Min** for heavy hitters — exact structures only where money or correctness demands it.”

## Exercise

**Design “unique viewers of a livestream” + “dedup notification sends.”**

1. Which sketch (or exact store) for each — and why?
2. What’s the user-visible risk of a Bloom false positive on notification dedup?
3. One sentence on merging HLLs from 10 partitions.
