# Document (MongoDB)

> Store **JSON-like documents** in collections — flexible schema, query nested fields, choose **embed vs reference**.

## Plain English

A document is a self-contained JSON object. Collections group similar documents. Schema can evolve field-by-field. The core design choice is **embed vs reference** — same problem as “aggregate boundaries” in DDD.

## Essentials (must-know for this topic)

### Embed vs reference

| | **Embed** | **Reference** |
|--|-----------|---------------|
| Shape | Nested array/object in parent | Store `author_id`; fetch separately |
| Read | One round trip for aggregate | More round trips / `$lookup` |
| Write | Update whole doc; size grows | Update independently |
| Use when | Data read/written **together**; bounded size | Shared entities; **unbounded** growth |
| Risk | 16MB doc limit; huge arrays | N+1-ish app joins |

**Rule of thumb:** embed line items on an order; reference users; don’t embed infinite comments.

### Mongo vocab

| Term | Meaning |
|------|---------|
| **Document** | JSON-like record (`BSON`) |
| **Collection** | Bag of documents (≈ table) |
| **`_id`** | Primary key (default ObjectId) |
| **Index** | Same idea as SQL — required for hot filters |
| **Multi-doc txn** | Possible (ACID since 4.x) but costlier — not default mindset |

### Indexing & query basics

| Pattern | Note |
|---------|------|
| Equality on `user_id`, `status` | B-tree indexes |
| Multikey on arrays | Index array values |
| Compound | Leftmost prefix applies |
| No index | Collection scan |

### Schema flexibility — with guardrails

| Do | Don’t |
|----|-------|
| Evolve fields additively | Dump unvalidated junk forever |
| Use schema validation when mature | Unbounded embedded arrays |
| Model around **access patterns** | Pretend it’s SQL with invisible joins |

## Why seniors get asked

Product teams love flexibility; seniors must police unbounded arrays, transactional needs, and index design.

## Simple example

```javascript
// Embed line items in an order
db.orders.insertOne({
  _id: "43",
  user_id: "7",
  status: "open",
  items: [{ sku: "TSHIRT", qty: 2, price_cents: 999 }]
});

db.orders.find({ user_id: "7", status: "open" });

// Reference pattern
db.posts.insertOne({ _id: "p1", author_id: "7", title: "Hello" });
db.users.findOne({ _id: "7" });
```

## When to use / when not / trade-offs

| Use documents when… | Prefer SQL/graph when… |
|---------------------|------------------------|
| Aggregate-oriented reads (order + items) | Heavy multi-entity transactions |
| Evolving schema / polymorphic attrs | Complex joins across many relations |
| Horizontal scale with shard key | Strict relational constraints |

**Trade-offs:** developer speed + natural aggregates vs weaker joins; embedding can duplicate or bloat documents (16MB limit in MongoDB).

## Common pitfalls

- Unbounded embedded arrays (comments forever in one doc)
- No indexes → collection scans
- Treating Mongo as “ schemaless dump” with no validation
- Multi-document transactions as the default (possible but not free)

## Interview trigger phrase

> “I’d embed data that’s read/written together as one aggregate, and reference entities that are shared or grow without bound.”

## Exercise

Model a blog post with likes and comments. When do you embed comments vs separate collection? What’s your cap strategy?
