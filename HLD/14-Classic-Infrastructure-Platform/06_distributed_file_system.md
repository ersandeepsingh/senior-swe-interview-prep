# Design a Distributed File System (GFS/HDFS-style) 🔴

> **Crux:** Split files into **chunks**, **replicate** chunks for durability, and keep a **metadata master** small/reliable — the hard part is metadata + re-replication, not raw disk.

## Clarify (say this first)

**Functional**
- Create / read / append (random write often limited)
- Large files (GB–TB); sequential throughput
- Directory namespace; permissions (light)
- Replication factor (default 3)

**Non-functional**
- Survive disk / node / rack failure
- High aggregate bandwidth
- Master HA (single logical namenode)
- Optimize for large sequential I/O, not tiny files

## Back-of-envelope

```text
Chunk size 64–128 MB (GFS/HDFS classic)
1 PB cluster, RF=3 → ~333 TB unique data
1 PB / 128 MB ≈ 8M chunks → metadata ~few hundred B/chunk → GBs in master RAM
Read 1 GB file ≈ 8–16 chunk RPCs + parallel replica reads
```

## API + data model

```text
create(path) / open(path) / delete(path)
read(handle, offset, len) / append(handle, data)
```

| Entity | Fields |
|--------|--------|
| File inode | `path`, `chunk_ids[]`, `length`, `mtime` |
| Chunk | `chunk_id`, `version`, `replica_locations[]` |
| Chunkserver | `id`, `disks`, `heartbeat`, `reports` |

## High-level architecture

```text
  Client
    │ 1) ask master for chunk locations / lease
    ▼
  Master (namenode)     ← namespace + chunk→replica map
    │
    │ 2) client R/W data plane directly
    ▼
  Chunkservers (datanodes)
  [CS1][CS2][CS3]...  RF replicas per chunk
         ▲
         └── heartbeats + block reports
```

## Deep dive: the crux

**Metadata:** master holds namespace tree + chunk map **in memory** (persist via edit log + checkpoints). Client talks master for metadata only; **data flows client ↔ chunkservers**.

**Replication:**
| Concern | Approach |
|---------|----------|
| Placement | diverse rack/AZ; write pipeline |
| Detect loss | heartbeats + block reports |
| Repair | master schedules re-replication to keep RF |
| Consistency | chunk version / lease for primary mutator (GFS) |

**Alternatives:** object store (S3) for simpler API; Ceph CRUSH for decentralized placement. **Pick for interview:** GFS/HDFS model — master metadata, chunk RF=3, secondary/HA master, append-friendly.

**Tiny files:** many files → metadata explosion — pack / HAR / avoid DFS for small objects.

**Write path (GFS-style):** client asks master for lease on last chunk; pipelines data through primary → secondaries; primary assigns offset. Reads can hit any replica with matching version.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Large chunks | Less metadata; sequential I/O | Internal fragmentation; slow small reads |
| Central master | Simple namespace; fast lookups | HA + size of metadata critical |
| RF=3 | Durability | 3× storage; write amplify |
| Client↔datanode data path | Throughput | Clients must know topology |
| Append-only / immutability | Simpler consistency | Harder random update |

## Failure modes & scale

- **Chunkserver death:** master under-replicated → copy chunks elsewhere
- **Master death:** HA standby + shared edits; cold start from checkpoint+log
- **Network partition:** stale replicas — version numbers; lease expiry
- **Corrupt block:** checksum fail → read other replica; re-replicate
- **Scale metadata:** federation / multiple namenodes; or external meta DB

## Interview trigger phrase

> “I’d chunk files (~64–128 MB), store **RF=3** on chunkservers, and keep the **namespace and chunk map on a HA master** — clients fetch locations from the master, then read/write data directly to chunkservers.”

## Exercise

1. Why is the data path client→chunkserver instead of through the master?  
2. RF drops from 3→2 after a rack outage — what does the master do, and what do you prioritize?  
3. 100M files of 10 KB each — why is this a bad fit and what would you change?
