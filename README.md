# Senior Software Engineer — Interview Preparation

A structured, pattern-first study repo for **Senior SWE** interview loops: coding (DSA), system design (HLD), and low-level design / machine coding (LLD).

The goal is not to collect random solutions, but to build **recognition** — when you see a problem, you should quickly name the pattern, state the trigger, and talk through time/space trade-offs out loud.

---

## What’s in this repo

| Area | Guide | Code |
|------|-------|------|
| **DSA** — algorithms & data structures | [DSA-Patterns.md](DSA/DSA-Patterns.md) | Python solutions by topic |
| **HLD** — high-level / system design | [HLD-Patterns-Senior-SWE.md](HLD/HLD-Patterns-Senior-SWE.md) | Playbook only (no code) |
| **LLD** — low-level design & OOP | [LLD-Patterns-Senior-SWE.md](LLD/LLD-Patterns-Senior-SWE.md) | Playbook only (no code) |

### DSA folder layout

```
DSA/
├── DSA-Patterns.md          # Coverage map: pattern → LeetCode refs (no solutions)
├── Two-Pointers/            # Implemented solutions
├── Graphs/
├── Trees/
├── DP/
├── misc/                    # Cross-cutting snippets (LRU, binary search, etc.)
└── Previous Asks/           # Past interview-style problems (company-specific)
```

Pattern playbooks use a difficulty legend:

- 🟢 Easy / warm-up
- 🟡 Medium / standard 45–60 min round
- 🔴 Hard / senior-signal

---

## How to use this repo

### 1. Start with the playbooks

Read the pattern guides first. Each entry maps a **single primary pattern** to a one-line problem prompt and a LeetCode (or classic design) reference. Use them as a **coverage checklist**, not a cram sheet.

- **DSA:** [DSA/DSA-Patterns.md](DSA/DSA-Patterns.md) — 24 pattern categories from Two Pointers through Design problems
- **HLD:** [HLD/HLD-Patterns-Senior-SWE.md](HLD/HLD-Patterns-Senior-SWE.md) — CAP, caching, sharding, messaging, classic designs (URL shortener, feed, etc.)
- **LLD:** [LLD/LLD-Patterns-Senior-SWE.md](LLD/LLD-Patterns-Senior-SWE.md) — SOLID, GoF patterns, concurrency, classic machine-coding problems

### 2. Drill by pattern, not by problem count

For each pattern, be able to answer:

1. **Trigger** — What in the problem statement signals this pattern?  
   *(e.g. sorted array + pair sum → two pointers; contiguous optimum → sliding window)*
2. **Approach** — High-level steps before you write code
3. **Complexity** — Time and space, and why
4. **Variants** — One easy and one hard follow-up from the playbook

### 3. Implement in the matching folder

Working solutions live under `DSA/<topic>/`. Naming convention: `NN_problem_name.py` (e.g. `03_container_with_most_water.py`). Run locally with Python 3:

```bash
python DSA/Two-Pointers/01_two_sum_ii.py
```

VS Code debug configs are in `.vscode/launch.json` if you use the IDE.

### 4. Prioritize for a Senior loop

Senior interviews lean **medium → hard** and reward clean, complexity-aware code over exotic algorithms.

**Highest ROI (DSA):**

1. Two Pointers, Sliding Window
2. Binary Search (especially search-on-answer)
3. Trees (DFS/BFS), Graphs (BFS/DFS, Union-Find, Topo Sort)
4. DP (knapsack, LIS, LCS, grid, decision/state)
5. Design: LRU cache, min stack, iterators, rate limiters *(often with concurrency follow-ups)*

**HLD focus:** requirements → estimation → API/data model → core components → scaling (cache, shard, async) → trade-offs (CAP, consistency, failure modes).

**LLD focus:** SOLID at the seams, right pattern for the problem (Strategy, Observer, State, Factory), thread-safety when asked.

---

## Study workflow (suggested)

| Week | Focus |
|------|--------|
| 1–2 | Two Pointers, Sliding Window, Binary Search + playbook skim |
| 3–4 | Trees, Graphs, Topo Sort, Union-Find |
| 5–6 | DP core patterns + Design (LRU, etc.) |
| Ongoing | 1–2 HLD classics/week; 1 LLD machine-coding/week |
| Last week | Weak patterns only; timed mocks; verbal trade-off practice |

---

## Contributing (personal use)

This is a personal prep repo. If you fork it:

- Keep **one primary pattern** per playbook entry
- Add solutions under the correct `DSA/<pattern>/` folder
- Prefer readable Python over golf; add a short docstring with problem link and complexity

---

## Disclaimer

`DSA/Previous Asks/` may contain problems from real interviews. Use ethically: learn the pattern, do not leak confidential interview content publicly.

---

## License

MIT — use and adapt freely for your own interview prep.
