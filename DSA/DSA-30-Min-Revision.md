# DSA 30-Min Rapid Revision

Most-asked patterns + problems for a senior SWE coding round.
Goal: pattern recognition + complexity, not full re-solves.

**How to use (30 min):**
1. For each problem: say the **trigger**, **approach (2–3 lines)**, **time/space**.
2. Only open a file if you blank — don’t re-code everything.
3. Tick ✅ as you go.

---

## Block 1 — Arrays & Windows (8 min)

| # | Pattern trigger | Problem | Complexity | File | ✅ |
|---|-----------------|---------|------------|------|---|
| 1 | Sorted array + pair/target | Two Sum II | O(n) / O(1) | `Two-Pointers/01_two_sum_ii.py` | ☐ |
| 2 | Unique triplets sum 0 | 3Sum | O(n²) / O(1) | `Two-Pointers/02_3sum.py` | ☐ |
| 3 | Max area between lines | Container With Most Water | O(n) / O(1) | `Two-Pointers/03_container_with_most_water.py` | ☐ |
| 4 | Contiguous substring, longest no repeats | Longest Substring Without Repeating | O(n) / O(k) | `Sliding-Window/02_longest_substring_without_repeating_characters.py` | ☐ |
| 5 | Contiguous, shortest ≥ target | Min Size Subarray Sum | O(n) / O(1) | `Sliding-Window/03_minimum_size_subarray_sum.py` | ☐ |
| 6 | Window containing all of t | Minimum Window Substring | O(n) / O(k) | `Sliding-Window/07_minimum_window_substring.py` | ☐ |

**Triggers to say out loud**
- Sorted + pair → opposite two pointers
- Contiguous subarray/substring optimum → sliding window
- Min window covering constraint → expand/shrink + freq map

---

## Block 2 — Binary Search & Heaps (5 min)

| # | Pattern trigger | Problem | Complexity | File | ✅ |
|---|-----------------|---------|------------|------|---|
| 7 | Sorted, find index | Binary Search | O(log n) | `Binary-Search/01_binary_search.py` | ☐ |
| 8 | Rotated sorted | Search in Rotated Sorted Array | O(log n) | `Binary-Search/03_search_in_rotated_sorted_array.py` | ☐ |
| 9 | Min/max under monotonic constraint | Koko Eating Bananas | O(n log M) | `Binary-Search/05_koko_eating_bananas.py` | ☐ |
| 10 | K-th / top frequent | Kth Largest / Top K Frequent | O(n log k) | `Top-K-Heaps/01_…` `02_…` | ☐ |

**Triggers**
- Answer space is monotonic (can finish / cannot) → binary search on answer
- Top-K streaming → heap of size k

---

## Block 3 — Trees (5 min)

| # | Pattern trigger | Problem | Complexity | File | ✅ |
|---|-----------------|---------|------------|------|---|
| 11 | Root→leaf path = target | Path Sum | O(n) | `Trees-DFS/01_path_sum.py` | ☐ |
| 12 | Height / depth | Max Depth | O(n) | `Trees-DFS/03_maximum_depth_of_binary_tree.py` | ☐ |
| 13 | Longest path (edges) | Diameter | O(n) | `Trees-DFS/04_diameter_of_binary_tree.py` | ☐ |
| 14 | Lowest common ancestor | LCA | O(n) | `Trees-DFS/05_lowest_common_ancestor.py` | ☐ |
| 15 | Level by level | Level Order | O(n) | `Trees-BFS/01_binary_tree_level_order_traversal.py` | ☐ |
| 16 | Rightmost per level | Right Side View | O(n) | `Trees-BFS/03_binary_tree_right_side_view.py` | ☐ |

**Triggers**
- Path / validate / construct → DFS recurse + return state
- Per-level / nearest leaf → BFS queue

---

## Block 4 — Graphs + Intervals (6 min)

| # | Pattern trigger | Problem | Complexity | File | ✅ |
|---|-----------------|---------|------------|------|---|
| 17 | Grid connected components | Number of Islands | O(mn) | `Graph-Patterns/01_number_of_islands.py` | ☐ |
| 18 | Multi-source spread | Rotting Oranges | O(mn) | `Graph-Patterns/03_rotting_oranges.py` | ☐ |
| 19 | Directed cycle / order | Course Schedule | O(V+E) | `Graph-Patterns/08_course_schedule.py` | ☐ |
| 20 | Connectivity count | Number of Provinces | O(n²) | `Union-Find/01_number_of_provinces.py` | ☐ |
| 21 | Overlap merge | Merge Intervals | O(n log n) | `Merge-Intervals/01_merge_intervals.py` | ☐ |
| 22 | Min rooms | Meeting Rooms II | O(n log n) | `Merge-Intervals/04_meeting_rooms_ii.py` | ☐ |

**Triggers**
- Grid land/water → DFS/BFS flood
- Prerequisites / order → topo (Kahn or DFS cycle)
- Provinces / friend circles → Union-Find or DFS components
- Overlaps → sort by start, then merge / sweep

---

## Block 5 — DP + Design (6 min)

| # | Pattern trigger | Problem | Complexity | File | ✅ |
|---|-----------------|---------|------------|------|---|
| 23 | Partition equal sum | Partition Equal Subset Sum | O(n·sum) | `Dynamic-Programming/01_partition_equal_subset_sum.py` | ☐ |
| 24 | Fewest coins | Coin Change | O(amount · coins) | `Dynamic-Programming/02_coin_change.py` | ☐ |
| 25 | Max contiguous sum | Maximum Subarray (Kadane) | O(n) | `Dynamic-Programming/05_maximum_subarray.py` | ☐ |
| 26 | Longest increasing | LIS | O(n log n) | `Dynamic-Programming/06_longest_increasing_subsequence.py` | ☐ |
| 27 | Grid min path | Min Path Sum | O(mn) | `Dynamic-Programming/12_minimum_path_sum.py` | ☐ |
| 28 | O(1) get/put eviction | LRU Cache | O(1) | `Design/01_lru_cache.py` | ☐ |
| 29 | O(1) min | Min Stack | O(1) | `Design/04_min_stack.py` | ☐ |

**Triggers**
- Optimal over choices / subproblems → DP (define state first)
- Cache eviction → HashMap + Doubly Linked List
- Running min with stack → dual stack / store (val, min)

---

## Bonus — say these if time left (optional)

| Problem | Why it shows up | File |
|---------|-----------------|------|
| Trapping Rain Water | Hard classic, two pointers or stack | `Two-Pointers/04_…` |
| Linked List Cycle | Fast/slow pointer | `Fast-Slow-Pointers/01_…` |
| Reverse Linked List | In-place pointer rewrite | `Linked-List-Reversal/01_…` |
| Daily Temperatures | Monotonic stack | `Monotonic-Stack/01_…` |
| Subarray Sum Equals K | Prefix + hashmap | `Prefix-Sum-Hashing/01_…` |
| Valid Parentheses | Stack basics | `Stacks-Queues/01_…` |
| Generate Parentheses | Backtracking template | `Backtracking/07_…` |

---

## Pattern cheat card (memorize)

| Hear this… | Reach for… |
|------------|------------|
| Sorted array + pair / container | Two pointers |
| Contiguous subarray / substring | Sliding window |
| Sorted / min feasible answer | Binary search (on index or answer) |
| Tree path / validate / LCA | DFS |
| Tree levels / shortest leaf | BFS |
| Grid islands / clone / multi-source | Graph BFS/DFS |
| Course order / prerequisites | Topological sort |
| Connectivity / merge accounts | Union-Find |
| Overlapping ranges | Sort + merge / sweep |
| Optimal count / max / min over choices | DP |
| Top-K / streaming median | Heap |
| Next greater / histogram | Monotonic stack |
| Eviction / O(1) design | HashMap + linked structure |

---

## After 30 min — spot gaps

Write the patterns you hesitated on:

1. _______________________________
2. _______________________________
3. _______________________________

Next session: re-solve **only those 3** from the linked files (no peeking at solutions — write approach first).
