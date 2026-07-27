# How to Approach an HLD Problem in the Interview

A **45–60 minute** system-design round is a conversation, not a whiteboard dump. Interviewers care that you: clarify, estimate, draw a simple working design, then deepen the hard parts and defend trade-offs.

Use this as a fixed script. Rehearse it out loud on one classic (URL shortener, News Feed, Chat, Ticket Booking).

---

## Minute budget (45–60 min)

| Step | Time | Goal |
|------|------|------|
| 1. Clarify & scope | 5–8 min | Functional + non-functional requirements; cut scope out loud |
| 2. Back-of-envelope | 3–5 min | QPS, storage, bandwidth — show the system is “big” or “not” |
| 3. API & data model | 5–7 min | Core endpoints + main entities / access patterns |
| 4. High-level design | 8–12 min | Boxes and arrows that satisfy the happy path |
| 5. Deep dive | 15–20 min | The 1–2 hardest parts (scale, consistency, realtime, search…) |
| 6. Scale, failure, trade-offs | 5–8 min | Bottlenecks, SPOFs, CAP, what you’d do next |
| Buffer / questions | 2–3 min | Leave room for interviewer redirects |

If they interrupt, follow them — don’t finish your script at the cost of ignoring a probe.

---

## Step 1 — Clarify & scope (5–8 min)

### What to do

1. Restate the problem in one sentence.
2. Ask **functional** questions (who, what actions, MVP).
3. Ask **non-functional** questions (scale, latency, consistency, availability).
4. Explicitly **cut scope**: “For v1 I’ll focus on X; I’ll defer Y unless you want it.”

### Ask these (adapt per problem)

**Functional**
- Who are the users? (end users, creators, admins, third parties)
- Core actions for MVP? (e.g. create short URL, redirect, optional analytics)
- Read-heavy or write-heavy?
- Mobile / web / both? Offline? Auth required?
- Any must-have features vs nice-to-have? (search, notifications, payments…)

**Non-functional (NFRs)**
- Scale: DAU / MAU, peak QPS, data size, growth
- Latency: p99 targets (e.g. redirect < 100 ms)
- Consistency: strong vs eventual OK?
- Availability: how bad is downtime?
- Durability: can we lose recent writes?
- Regions: single region OK for v1?

### Phrases that sound senior

> “I’ll assume X users and Y QPS unless you have numbers — I’ll size from that.”

> “For the interview I’ll design the core path first; we can add Z if time allows.”

> “Is eventual consistency OK for the feed, or do users need read-your-writes?”

### Tiny example (URL shortener)

- MVP: create short URL, redirect, optional custom alias
- Out of scope for now: fancy analytics UI, A/B experiments, enterprise SSO
- NFRs: mostly reads on redirect; low latency; high availability; short codes unique

---

## Step 2 — Back-of-envelope (3–5 min)

Show you can size the problem. Round numbers; say assumptions out loud.

### Template

1. **Users / traffic** → daily active → peak QPS (often peak ≈ 2–5× average)
2. **Reads vs writes** ratio
3. **Storage** = objects × size × retention × replication
4. **Bandwidth** if media is involved

### Rough formulas

```text
avg QPS  ≈ daily_ops / 86_400
peak QPS ≈ avg × 2..5

storage  ≈ records × avg_bytes × years × replicas
```

### Example (URL shortener)

```text
100M new URLs / month ≈ 40 writes/s avg → ~200 peak writes/s
redirects 100× writes → ~4K avg reads/s → ~20K peak reads/s
URL mapping ~500 B → 100M × 500 B ≈ 50 GB / month (plus indexes/replicas)
```

Say: “Reads dominate → cache + CDN-friendly redirect path; DB write path is smaller.”

**Don’t** spend 15 minutes on arithmetic. One clear sizing pass is enough.

---

## Step 3 — API & data model (5–7 min)

### APIs (sketch, not OpenAPI perfection)

List 3–6 core endpoints with method + purpose:

```text
POST   /urls          → create short URL
GET    /{code}        → redirect (302/301)
GET    /urls/{code}   → metadata (optional)
DELETE /urls/{code}   → deactivate (optional)
```

Mention auth if relevant (who can create/delete).

### Data model

- Name **entities** and the fields that matter for access patterns
- Call out **primary keys**, uniqueness, and what you query by
- Don’t draw every table — only what the design hangs on

```text
UrlMapping
  short_code  PK (or unique)
  long_url
  user_id
  created_at
  expires_at?
```

### Access patterns (say this out loud)

> “Hot path is `short_code → long_url` by primary key / unique index. Writes are inserts with uniqueness on code.”

Access patterns drive DB choice more than “SQL vs NoSQL” slogans.

---

## Step 4 — High-level design (8–12 min)

Draw a **simple** diagram that works for the happy path. Start boring; complexity comes in Step 5.

### Default skeleton (most problems)

```text
Client → DNS/CDN → Load Balancer → API / App servers (stateless)
                         ↓
              Cache (Redis)     DB (primary + replicas)
                         ↓
              Object store / Queue / Search  (only if needed)
```

### How to narrate while drawing

1. Client hits LB / API gateway
2. Stateless app tier handles auth + business logic
3. Write path → DB (and maybe queue for async work)
4. Read path → cache, then DB
5. Heavy/async work → workers + queue
6. Media → object storage + CDN

### Rules

- **One happy path end-to-end** before sharding Kafka and multi-region
- Label arrows: “write”, “read”, “async”
- Prefer **stateless** app servers so you can scale horizontally
- Name 1–2 concrete technologies only when helpful (“Postgres + Redis”); don’t name-drop the whole AWS catalog

### Example (URL shortener — first cut)

```text
Browser → LB → URL Service
                  ├─ generate code
                  ├─ write mapping → DB
                  └─ on redirect: Cache → DB → 302 Location
```

---

## Step 5 — Deep dive (15–20 min)

This is where seniors win. Pick the **load-bearing hard part** for *this* problem and go deep.

### Common deep-dive themes by problem type

| Problem flavor | Likely deep dive |
|----------------|------------------|
| URL shortener / unique IDs | Code generation, uniqueness, collisions, caching redirects |
| News feed | Fan-out on write vs read, ranking, timeline storage |
| Chat / notifications | WebSockets, fan-out, presence, delivery guarantees |
| Ticket / seat booking | Inventory locking, idempotency, oversell prevention |
| Search | Indexing pipeline, ranking, eventual consistency with source of truth |
| Video / media | Upload, transcoding, CDN, adaptive bitrate |
| Rate limiter | Algorithm (token bucket / sliding window), distributed counters |

### How to deep dive

1. State the bottleneck: “Redirect QPS and unique code generation are the hard parts.”
2. Propose **v1 simple** approach
3. Show where it breaks at scale
4. Evolve: cache, shard key, queue, replication, etc.
5. Call out **consistency / failure** behavior

### Example deep dives (URL shortener)

**Code generation**
- Base62 of counter / snowflake / hash+retry
- Uniqueness: DB unique constraint + retry, or pre-allocated ranges

**Redirect path**
- Cache `code → url` (TTL + invalidate on delete)
- 301 vs 302 (caching vs analytics control)

**Scale reads**
- DB read replicas + cache; maybe edge/CDN for hot codes later

---

## Step 6 — Scale, failure modes & trade-offs (5–8 min)

Proactively cover what seniors are expected to raise:

### Scale checklist

- Where is the bottleneck first? (CPU, DB connections, single shard, cache stampede)
- How do we scale that tier? (horizontal app, read replicas, shard by key)
- What is the shard / partition key and why?

### Failure checklist

- DB primary down → failover / promote replica
- Cache down → fall through to DB (and protect DB with limits)
- Queue lag → backpressure, delay non-critical features
- Duplicate requests → idempotency keys

### Trade-off language (use CAP / PACELC lightly, correctly)

> “Redirects can be slightly stale if we cache aggressively — I’ll take AP-ish behavior on reads. Creating a short URL needs uniqueness — that’s a CP-ish write on the mapping.”

### What you’d do in v2 (show judgment)

- Multi-region active-active
- Stronger analytics pipeline
- Custom domains, teams, abuse detection

Don’t build v2 unless asked — just show you know it exists.

---

## Communication tips (senior signal)

1. **Talk while drawing** — silence feels like you’re stuck.
2. **Drive, but check in** — “I’ll cache redirects next — sound good?”
3. **One idea at a time** — finish a component before adding five more boxes.
4. **Trade-offs > buzzwords** — every choice: *what you gain / what you give up*.
5. **Admit unknowns** — “I’d verify p99 with a load test; for now I’m targeting <100 ms.”
6. **Follow the interviewer** — if they say “focus on fan-out,” drop the CDN digression.

---

## Anti-patterns (avoid these)

| Anti-pattern | Do instead |
|--------------|------------|
| Jump straight to microservices + Kafka | Start with a modular monolith / few services that serve MVP |
| No requirements, pure tech dump | Clarify + scope first |
| Perfect SQL schema, no scale story | Access patterns + QPS first |
| Ignoring failure | Say what happens when cache/DB/queue dies |
| Over-precision in estimates | Order-of-magnitude is enough |
| Never asking questions | Design is collaborative |

---

## One-page cheat sheet (memorize)

```text
1. Clarify (functional + NFR) → cut scope
2. Estimate (QPS, storage, read/write ratio)
3. API + entities + access patterns
4. Simple HLD (client → LB → app → cache/DB → async if needed)
5. Deep dive 1–2 hard parts
6. Scale, failures, trade-offs, v2 ideas
```

---

## Practice loop

1. Pick a classic: URL shortener, Pastebin, News Feed, WhatsApp, Uber, YouTube, Ticketmaster, Rate limiter, Notification system.
2. Time-box 45 minutes with this script.
3. Afterward, ask: Did I clarify? Did I estimate? Did I have a working HLD before deep dive? Did I name trade-offs?
4. Cross-check concepts in [HLD-Patterns-Senior-SWE.md](HLD-Patterns-Senior-SWE.md).

---

## Interview-ready opener (say this almost every time)

> “I’ll clarify requirements and NFRs, do a quick capacity estimate, outline APIs and the data model, draw a simple architecture for the core flow, then deep-dive the hardest scaling/consistency parts and walk through failures and trade-offs. I’ll keep v1 scoped and call out what I’d defer.”
