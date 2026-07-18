# Partitioning & Sharding

> When one node can’t hold or serve all data, you **split** by a key. Partitioning (logical split) + sharding (split across machines) is how databases scale horizontally — the shard key choice is the design.

## Plain English

| Strategy | How you place a row | Strength | Weakness |
|----------|---------------------|----------|----------|
| **Range** | Key falls in `[A–M]` → shard 1 | Range scans easy | Hotspots at end of range |
| **Hash** | `hash(key) % N` → shard | Even load | No efficient cross-shard range |
| **Directory** | Lookup table: key → shard | Flexible remapping | Directory is critical path |
| **Geo** | User region → regional shard | Locality / residency | Cross-region queries hard |

```text
  Client / router
        │
        ▼
  ┌─────────── shard key ───────────┐
  │ range │ hash │ directory │ geo  │
  └───┬───┴───┬──┴─────┬─────┴──┬───┘
      ▼       ▼        ▼        ▼
   ShardA  ShardB   ShardC   ShardD
```

## Simple example

**Users and posts for a social app.**

| Key choice | Behavior |
|------------|----------|
| Shard by `user_id` (hash) | All of Alice’s data on one shard — easy “her profile” |
| Shard by `post_id` (hash) | User’s posts scatter — “my posts” is scatter-gather |
| Range by `created_at` | New posts hammer the newest range → hotspot |

```text
  hash(user_id) % 4
  Alice → Shard 2   (followers, posts meta colocated)
  Bob   → Shard 0

  Global “trending” query → fan-out to all shards or separate index
```

## Why prefer one over the other

| Prefer **hash** when… | Prefer **range** when… | Prefer **directory / geo** when… |
|-----------------------|------------------------|----------------------------------|
| Even QPS matters most | Time-series / key ranges dominate | Need controlled moves or data residency |
| Point lookups by id | `WHERE ts BETWEEN …` on one shard | Regulated geo, or rebalance without rehash |

**Why not shard too early?** Operational pain (joins, transactions, resharding) arrives the day you shard. Vertical scale + read replicas first is often enough.

**Why not random shard key?** Every user-scoped query becomes multi-shard.

### Real systems (interview name-drops)

- **Hash/range shards:** Vitess, Citus, MongoDB sharding, Cassandra token rings.
- **Directory:** Many custom routers; DynamoDB partition map (managed).
- **Geo:** Regional Postgres / Cosmos DB multi-region accounts.

## Trade-offs

| Choice | You gain | You give up |
|--------|----------|-------------|
| Hash sharding | Balanced load | Painful range queries; reshuffle on naive `% N` |
| Range sharding | Efficient scans | Hot partitions (celebrity / latest time) |
| Directory-based | Move keys without full rehash | Extra hop; directory HA |
| Geo partitioning | Latency + compliance | Cross-region consistency / fan-out |

**Common interview trap:** Sharding by `email` prefix or auto-increment alone without discussing hotspots. Seniors pick a key that **matches the primary access path** and name the cross-shard tax.

## Interview trigger phrase

> “I’d shard by the **dominant lookup key** — usually `user_id` with **hash** for even load — and keep global queries on a separate index or accept scatter-gather.”

## Exercise

**Shard a multiplayer game’s player inventory + leaderboards.**

1. Choose a shard key for inventory; explain why `item_id` is probably wrong.  
2. Global top-100 leaderboard — range shard on score or something else? Argue.  
3. One sentence on what breaks for “trade item between two players on different shards.”
