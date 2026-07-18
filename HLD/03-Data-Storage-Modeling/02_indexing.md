# Indexing

> An index is a **side structure** that turns “scan the whole table” into “jump near the row.” Wrong index = slow writes and wasted disk; missing index = death by full scan.

## Plain English

| Index type | How it finds data | Best for |
|------------|-------------------|----------|
| **B-tree** | Sorted tree of keys | Range queries, `ORDER BY`, most SQL defaults |
| **Hash** | `hash(key) → bucket` | Exact equality only (`WHERE id = ?`) |
| **Inverted** | Term → list of doc IDs | Full-text / search (“contains word”) |

```text
  Table (heap / clustered)
  ┌────┬────────┬────────┐
  │ id │ email  │ city   │
  └────┴────────┴────────┘
         ▲           ▲
         │           │
   B-tree on email   B-tree on city
   (unique lookups)  (filter + sort)

  Search corpus
  "latency" ──► [doc3, doc9, doc41]   ← inverted index
```

## Simple example

**Users table:** find by email, list users in Mumbai sorted by signup.

```text
  SELECT * FROM users WHERE email = 'a@b.com';
       → unique B-tree / hash on email  (point lookup)

  SELECT * FROM users WHERE city = 'Mumbai' ORDER BY created_at;
       → B-tree (city, created_at) or city + sort
       → hash index cannot help ORDER BY / ranges
```

**Product search:** “wireless headphones under 2000”

```text
  Inverted index:  wireless → …  headphones → …
  Plus filter attributes in DB or search engine (Elasticsearch)
```

## Why prefer one over the other

| Prefer **B-tree** when… | Prefer **hash** when… | Prefer **inverted** when… |
|-------------------------|------------------------|---------------------------|
| Ranges, prefixes, sorting | Only exact match, high QPS | Text search, relevance ranking |
| Default SQL secondary index | Some in-memory / KV equality | Search products, logs, docs |

**Why not index every column?** Each index slows writes (update index on INSERT/UPDATE/DELETE) and uses disk. Index what you **query**.

**Why not only hash?** No range scans — `BETWEEN`, `>`, prefix `LIKE 'san%'` fail.

### Real systems (interview name-drops)

- **B-tree / B+tree:** Postgres, InnoDB, most RDBMS primary/secondary.
- **Hash:** Redis hashes conceptually; some DB hash indexes; DynamoDB partition key hashing.
- **Inverted:** Elasticsearch / OpenSearch, Lucene, Solr; Postgres GIN for full-text/JSON.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Add B-tree on hot filter | Fast reads | Slower writes; more storage |
| Covering / composite index | Avoid table lookups | Larger index; careful column order |
| Hash-only equality index | Tiny / fast point get | No ranges or ordering |
| Inverted / search cluster | Rich text queries | Eventual sync, ops complexity, cost |

**Common interview trap:** “We’ll add indexes later.” Seniors sketch **which columns** and whether the index is **unique**, **composite**, or **covering** for the top 3 queries.

## Interview trigger phrase

> “I’d use a **B-tree** for equality and range filters, avoid hash when we need ranges, and push full-text to an **inverted index** (Elasticsearch) rather than `LIKE '%foo%'` on the primary DB.”

## Exercise

**Design indexes for a URL shortener + analytics.**

1. For `GET /{code}` resolving to a long URL — which index type and on which column?  
2. For “top 10 codes by clicks in last 24h” — what breaks if you only have a hash index on `code`?  
3. Say one sentence on write cost if you index every analytics dimension the PM might filter on someday.
