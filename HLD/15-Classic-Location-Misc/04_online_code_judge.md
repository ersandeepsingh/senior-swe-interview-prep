# Design an Online Code Judge 🟡

> **Crux:** Accept submissions asynchronously and run them in a **hard sandbox** (CPU/mem/network/FS isolation) — queue + isolation matter more than the web UI.

## Clarify (say this first)

**Functional**
- Submit code; multiple languages; run against hidden tests
- Verdicts: AC / WA / TLE / MLE / RE / CE
- Contests: rate limits; plagiarism (optional)
- Show sample diffs carefully (no full hidden leak)

**Non-functional**
- Untrusted code — assume hostile
- Queue latency under contest spikes
- Fair CPU time; deterministic limits
- Scale workers horizontally

## Back-of-envelope

```text
Contest: 10k users × 1 submit/min peak → ~170 submits/s
Avg run: 2 s CPU × 50 tests → ~100 s CPU / submit worst case
  → need ~17k CPU-cores at pathological peak → cap tests, pool, queue
Practical: 500–2k workers; queue absorbs spike; p50 wait seconds–minutes
Artifact store: code + logs + binaries for days
```

## API + data model

```text
POST /submissions     {problem_id, lang, source}
GET  /submissions/{id} → status, verdict, time, memory
GET  /problems/{id}
```

| Entity | Fields |
|--------|--------|
| Submission | `id`, `user`, `problem`, `lang`, `status`, `verdict` |
| Job | `submission_id`, `tests[]`, `limits` |
| Worker | `id`, `langs`, `busy` |

## High-level architecture

```text
  Web API
     │
     ▼
  Submission DB + Object store (source)
     │
     ▼
  Queue (Kafka / SQS)
     │
     ▼
  Judge workers
     │  compile → sandbox run per test → compare
     ▼
  Results writer ──► DB / WS notify user

  Images: language toolchains; seccomp / gVisor / VMs
```

## Deep dive: the crux

**Async execution + isolation:**
| Layer | Purpose |
|-------|---------|
| **Queue** | Decouple spike from capacity; priority for contests |
| **Container + seccomp/AppArmor** | Limit syscalls |
| **cgroups** | CPU time, memory, PIDs |
| **Network off / no docker.sock** | Block exfil / escape assist |
| **gVisor / Firecracker / VM** | Stronger isolation for multi-tenant |

**Pipeline:** compile once → run tests sequentially or pooled → stop on first WA if policy allows. **Idempotent workers:** submission_id as job key; retries safe. **Pick:** SQS/Kafka + Firecracker/gVisor workers; never run on API hosts.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Strong VM isolation | Security | Density / cold start |
| Shared kernel containers | Density | Larger escape risk |
| Early-stop tests | Throughput | Slightly less telemetry |
| Sync judge in API | Simple | Melts under contests |
| More worker langs images | UX | Image sprawl / CVE surface |

## Failure modes & scale

- **Poison / fork bomb:** cgroup PIDs + timeout; kill cgroup
- **Worker compromise:** ephemeral VMs; no secrets; rebuild from golden image
- **Queue backup:** autoscale workers; show position in queue
- **Flaky TLE:** isolate noisy neighbors; pin CPU; retry once
- **Answer leak:** separate judge network; audit logs; watermark tests

## Interview trigger phrase

> “Submissions go to a **queue**, and **sandboxed workers** compile and run tests with **cgroup + syscall/network lockdown** — the API never executes user code.”

## Exercise

1. Contest spike 100× — what saturates first and how does the user-visible status degrade?  
2. Why “Docker with default settings” is not enough for a public judge.  
3. Design idempotent retry when a worker dies mid-test suite.
