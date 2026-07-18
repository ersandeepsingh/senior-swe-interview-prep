# Conflict Resolution

> When replicas diverge, something must **win or merge**. **LWW** picks a winner; **CRDTs** merge mathematically so concurrent updates commute.

## Plain English

After a partition (or offline edit), two replicas may both accept writes. On heal, you **resolve**:

| Strategy | Idea | Best for |
|----------|------|----------|
| **LWW** (last-write-wins) | Highest timestamp / version wins | Simple fields; loss OK |
| **App merge** | Business rules (union carts) | Domain-specific |
| **CRDTs** | Types designed to merge (G-Counter, OR-Set, LWW-Register…) | Collaborative / offline |
| **Manual / flag** | Surface conflict to user | Docs, rare high-value merges |

```text
          Replica 1                Replica 2
          likes=5                  likes=7
               \                     /
                \   partition heal  /
                 v                 v
            ┌─────────────────────────┐
            │  Resolve:               │
            │  LWW → keep 7 (if ts)   │
            │  CRDT counter → merge   │
            │  per type rules         │
            └─────────────────────────┘
```

## Simple example

**Collaborative todo list**

- **LWW on whole list JSON:** one user’s add can wipe the other’s add. Bad.
- **OR-Set CRDT:** both adds survive; concurrent delete+add has defined rules (tombstones / dots).
- **LWW on a single “theme color” field:** fine — last picker wins.

**Shopping cart:** often **union of items** (app-level merge) or set CRDT — never blind LWW on the whole blob.

```text
  A: {milk}     B: {eggs}     LWW(blob) may drop one
                              merge/OR-Set → {milk, eggs} ✓
```

## Why prefer one over the other

| Prefer **LWW** when… | Prefer **CRDTs / merge** when… |
|----------------------|--------------------------------|
| Single field, low contention | Concurrent edits must not drop data |
| Ops simplicity, rare conflicts | Offline-first, multi-region active-active |
| Cache invalidation markers | Counters, sets, collaborative text (special CRDTs) |

**Why not always CRDT?** Complexity, larger payloads, not every type has a clean CRDT. **Bank balance** usually wants single-writer / consensus — not a naive G-Counter (increments only; debits need different design).

### Real systems

- **Cassandra LWW** columns; **Riak** sibling values; **Redis CRDTs** (enterprise); **Automerge / Yjs** for collab docs.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| LWW | Simple, fast | Silent loss of concurrent updates |
| CRDT | Convergence without coordinator | Memory/metadata; learning curve |
| Manual conflict UI | Human picks for docs | Bad UX at scale; not for money |
| Single primary | No merge needed | Availability / geo latency |

**Trap:** “We’ll use CRDTs for the ledger.” Money usually wants **single-writer / consensus**, not merge-friendly AP. CRDTs shine for presence, likes, shopping sets, configs.

## Interview trigger phrase

> “For active-active I’d **LWW** only on low-value fields; for carts/collaborative state I’d use **CRDTs or explicit merge** — and keep the payment ledger on a single primary.”

## Exercise

**Design multi-region “user preferences” + “wallet balance.”**

1. Pick LWW vs CRDT (or neither) for each — justify.
2. What user-visible bug does LWW cause on a shopping cart blob?
3. One sentence: how tombstones / version vectors relate to deletes in set CRDTs.
