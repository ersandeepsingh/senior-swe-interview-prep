# DSA Pattern Playbook — Senior SWE Interview Prep

Organized by **primary pattern category → sub-patterns → 1-line prompt + LeetCode reference**.
Each question is mapped to its **most critical** pattern (not every micro-technique it happens to use).
No solutions — this is a coverage map so you know what to drill.

Legend: 🟢 Easy · 🟡 Medium · 🔴 Hard

---

## 1. Two Pointers

- **Opposite ends (converging)** — Pair with target sum in sorted array → Two Sum II (LC 167 🟡)
- **Triplets / k-sum** — Find all unique triplets summing to zero → 3Sum (LC 15 🟡)
- **Container/area** — Max water between two lines → Container With Most Water (LC 11 🟡)
- **Trapping** — Water trapped between bars → Trapping Rain Water (LC 42 🔴)
- **Same-direction (read/write)** — Remove duplicates in place → Remove Duplicates from Sorted Array (LC 26 🟢)
- **Partitioning (Dutch flag)** — Sort array of 0s/1s/2s → Sort Colors (LC 75 🟡)
- **Palindrome checks** — Valid palindrome ignoring non-alnum → Valid Palindrome (LC 125 🟢)
- **String compare with skips** — Compare with backspaces → Backspace String Compare (LC 844 🟢)

## 2. Sliding Window

- **Fixed-size window** — Max average of k-length subarray → Max Average Subarray I (LC 643 🟢)
- **Variable window (longest)** — Longest substring without repeats → Longest Substring Without Repeating Characters (LC 3 🟡)
- **Variable window (shortest)** — Smallest subarray ≥ target sum → Minimum Size Subarray Sum (LC 209 🟡)
- **Window + frequency map** — Longest substring after k replacements → Longest Repeating Character Replacement (LC 424 🟡)
- **Anagram / permutation window** — Find all anagrams of p in s → Find All Anagrams in a String (LC 438 🟡)
- **Window with at-most-k constraint** — Fruit into baskets (≤2 types) → Fruit Into Baskets (LC 904 🟡)
- **Hardest window (min-window)** — Smallest window containing all of t → Minimum Window Substring (LC 76 🔴)

## 3. Fast & Slow Pointers (Cycle Detection)

- **Linked list cycle** — Detect if list has a loop → Linked List Cycle (LC 141 🟢)
- **Cycle entry point** — Find node where cycle begins → Linked List Cycle II (LC 142 🟡)
- **Middle of list** — Find midpoint in one pass → Middle of the Linked List (LC 876 🟢)
- **Duplicate via cycle** — Find repeated number, O(1) space → Find the Duplicate Number (LC 287 🟡)
- **Number theory cycle** — Detect happy-number loop → Happy Number (LC 202 🟢)

## 4. In-place Linked List Reversal

- **Full reversal** — Reverse entire list → Reverse Linked List (LC 206 🟢)
- **Sub-list reversal** — Reverse between positions m..n → Reverse Linked List II (LC 92 🟡)
- **K-group reversal** — Reverse nodes in groups of k → Reverse Nodes in k-Group (LC 25 🔴)
- **Reorder** — Weave first/last halves → Reorder List (LC 143 🟡)
- **Swap pairs** — Swap adjacent nodes → Swap Nodes in Pairs (LC 24 🟡)

## 5. Merge Intervals

- **Merge overlapping** — Combine overlapping intervals → Merge Intervals (LC 56 🟡)
- **Insert into sorted intervals** — Add and merge new interval → Insert Interval (LC 57 🟡)
- **Interval intersection** — Intersect two sorted lists → Interval List Intersections (LC 986 🟡)
- **Min rooms / resources (sweep line)** — Min meeting rooms needed → Meeting Rooms II (LC 253 🟡)
- **Can-attend check** — Any overlap at all → Meeting Rooms (LC 252 🟢)
- **Non-overlap removal** — Min intervals to erase → Non-overlapping Intervals (LC 435 🟡)

## 6. Cyclic Sort (Numbers in a Range)

- **Find missing** — Missing number in 0..n → Missing Number (LC 268 🟢)
- **All missing** — All numbers disappeared in 1..n → Find All Numbers Disappeared in an Array (LC 448 🟢)
- **Find duplicate(s)** — All duplicates in place → Find All Duplicates in an Array (LC 442 🟡)
- **First missing positive** — Smallest missing positive int → First Missing Positive (LC 41 🔴)
- **Set mismatch** — The duplicated + missing pair → Set Mismatch (LC 645 🟢)

## 7. Binary Search

- **Classic** — Search in sorted array → Binary Search (LC 704 🟢)
- **Boundary / first-last** — First and last position of target → Find First and Last Position (LC 34 🟡)
- **Rotated array** — Search in rotated sorted array → Search in Rotated Sorted Array (LC 33 🟡)
- **Peak finding** — Find any peak element → Find Peak Element (LC 162 🟡)
- **Search on answer space** — Min eating speed under time limit → Koko Eating Bananas (LC 875 🟡)
- **Split / capacity minimization** — Min largest sum of k splits → Split Array Largest Sum (LC 410 🔴)
- **Median of two arrays** — kth/median via partition search → Median of Two Sorted Arrays (LC 4 🔴)
- **2D matrix search** — Search sorted matrix → Search a 2D Matrix (LC 74 🟡)

## 8. Top-K Elements / Heaps

- **K largest/smallest** — Kth largest in array → Kth Largest Element in an Array (LC 215 🟡)
- **Top-K frequent** — K most frequent elements → Top K Frequent Elements (LC 347 🟡)
- **K closest** — K points closest to origin → K Closest Points to Origin (LC 973 🟡)
- **Streaming median (two heaps)** — Median from a data stream → Find Median from Data Stream (LC 295 🔴)
- **Scheduling with heap** — Reorganize / task cooldown → Task Scheduler (LC 621 🟡)
- **Sliding window max (deque/heap)** — Max in each window → Sliding Window Maximum (LC 239 🔴)

## 9. K-way Merge

- **Merge sorted lists** — Merge k sorted linked lists → Merge k Sorted Lists (LC 23 🔴)
- **Smallest range across lists** — Range covering one from each list → Smallest Range Covering Elements from K Lists (LC 632 🔴)
- **Kth smallest in matrix** — Sorted-rows matrix → Kth Smallest Element in a Sorted Matrix (LC 378 🟡)
- **Kth smallest sum** — Smallest sums from two arrays → Find K Pairs with Smallest Sums (LC 373 🟡)

## 10. Backtracking (Subsets / Permutations / Combinations)

- **Subsets** — All subsets of a set → Subsets (LC 78 🟡)
- **Permutations** — All orderings → Permutations (LC 46 🟡)
- **Combinations sum** — Combos summing to target → Combination Sum (LC 39 🟡)
- **Partition** — Palindrome partitioning → Palindrome Partitioning (LC 131 🟡)
- **Grid search / word** — Word exists in grid → Word Search (LC 79 🟡)
- **Constraint solving** — Place N queens → N-Queens (LC 51 🔴)
- **Parentheses generation** — All valid combinations → Generate Parentheses (LC 22 🟡)
- **Phone letter combos** — Digit → letter mapping → Letter Combinations of a Phone Number (LC 17 🟡)

## 11. Trees — DFS

- **Path sum / root-to-leaf** — Any root-leaf path equals target → Path Sum (LC 112 🟢)
- **Max path (any node)** — Max path sum anywhere → Binary Tree Maximum Path Sum (LC 124 🔴)
- **Depth / height** — Max depth → Maximum Depth of Binary Tree (LC 104 🟢)
- **Diameter** — Longest path between nodes → Diameter of Binary Tree (LC 543 🟢)
- **LCA** — Lowest common ancestor → LCA of a Binary Tree (LC 236 🟡)
- **BST validation** — Is valid BST → Validate Binary Search Tree (LC 98 🟡)
- **Kth in BST (in-order)** — Kth smallest in BST → Kth Smallest Element in a BST (LC 230 🟡)
- **Construct from traversals** — Build from preorder+inorder → Construct Binary Tree from Preorder and Inorder (LC 105 🟡)
- **Serialize / deserialize** — Encode & rebuild tree → Serialize and Deserialize Binary Tree (LC 297 🔴)

## 12. Trees — BFS (Level Order)

- **Level order** — Values grouped by level → Binary Tree Level Order Traversal (LC 102 🟡)
- **Zigzag** — Alternate direction per level → Binary Tree Zigzag Level Order Traversal (LC 103 🟡)
- **Right side view** — Rightmost node per level → Binary Tree Right Side View (LC 199 🟡)
- **Connect level pointers** — Populate next-right pointers → Populating Next Right Pointers (LC 116 🟡)
- **Min depth** — Shallowest leaf → Minimum Depth of Binary Tree (LC 111 🟢)

## 13. Graphs

- **DFS/BFS connected components** — Count islands in grid → Number of Islands (LC 200 🟡)
- **Flood fill / region** — Fill / capture surrounded regions → Surrounded Regions (LC 130 🟡)
- **Multi-source BFS** — Rotting oranges spread → Rotting Oranges (LC 994 🟡)
- **Clone graph** — Deep copy a graph → Clone Graph (LC 133 🟡)
- **Shortest path (unweighted BFS)** — Shortest transformation → Word Ladder (LC 127 🔴)
- **Dijkstra (weighted)** — Cheapest path within k stops → Cheapest Flights Within K Stops (LC 787 🟡)
- **Union-Find connectivity** — Number of provinces → Number of Provinces (LC 547 🟡)
- **Cycle detection (directed)** — Course schedule feasibility → Course Schedule (LC 207 🟡)
- **Bellman-Ford / grid Dijkstra** — Min effort path in grid → Path With Minimum Effort (LC 1631 🟡)

## 14. Topological Sort

- **Ordering feasibility** — Can finish all courses → Course Schedule (LC 207 🟡)
- **Produce an order** — Valid course order → Course Schedule II (LC 210 🟡)
- **Lexicographic from constraints** — Alien dictionary order → Alien Dictionary (LC 269 🔴)
- **Layered removal (BFS/Kahn)** — Min height trees roots → Minimum Height Trees (LC 310 🟡)
- **Sequence reconstruction** — Unique topo order check → Sequence Reconstruction (LC 444 🟡)

## 15. Union-Find (Disjoint Set)

- **Connectivity count** — Provinces / friend circles → Number of Provinces (LC 547 🟡)
- **Redundant edge** — Edge forming a cycle → Redundant Connection (LC 684 🟡)
- **Accounts merge** — Union emails by owner → Accounts Merge (LC 721 🟡)
- **Grid islands (dynamic)** — Islands as cells added → Number of Islands II (LC 305 🔴)
- **Equations consistency** — Satisfiability of equality eqs → Satisfiability of Equality Equations (LC 990 🟡)

## 16. Dynamic Programming

- **0/1 Knapsack** — Partition into equal-sum subsets → Partition Equal Subset Sum (LC 416 🟡)
- **Unbounded knapsack** — Fewest coins for amount → Coin Change (LC 322 🟡)
- **Fibonacci-style / climbing** — Ways to climb stairs → Climbing Stairs (LC 70 🟢)
- **House robber (non-adjacent)** — Max non-adjacent sum → House Robber (LC 198 🟡)
- **Kadane (max subarray)** — Largest contiguous sum → Maximum Subarray (LC 53 🟡)
- **LIS** — Longest increasing subsequence → Longest Increasing Subsequence (LC 300 🟡)
- **LCS (2-string DP)** — Longest common subsequence → Longest Common Subsequence (LC 1143 🟡)
- **Edit distance** — Min ops to convert strings → Edit Distance (LC 72 🟡)
- **String matching / wildcards** — Regex/wildcard match → Regular Expression Matching (LC 10 🔴)
- **Palindromic substrings** — Count/longest palindromes → Longest Palindromic Substring (LC 5 🟡)
- **Interval DP** — Max coins bursting balloons → Burst Balloons (LC 312 🔴)
- **Grid path DP** — Min path sum in grid → Minimum Path Sum (LC 64 🟡)
- **Decision/state DP** — Best time to buy/sell w/ cooldown → Best Time to Buy and Sell Stock with Cooldown (LC 309 🟡)
- **Bitmask DP** — Shortest path visiting all nodes → Shortest Path Visiting All Nodes (LC 847 🔴)
- **Weighted scheduling DP** — Cost-based ticket buying → Minimum Cost For Tickets (LC 983 🟡)

## 17. Greedy

- **Jump / reachability** — Can reach last index → Jump Game (LC 55 🟡)
- **Interval scheduling** — Max non-overlapping intervals → Non-overlapping Intervals (LC 435 🟡)
- **Balloon bursting (min arrows)** — Min arrows to burst → Minimum Number of Arrows (LC 452 🟡)
- **Gas station circuit** — Start index to complete loop → Gas Station (LC 134 🟡)
- **Partition labels** — Split into max parts → Partition Labels (LC 763 🟡)
- **Rearrange with constraint** — No two adjacent equal → Reorganize String (LC 767 🟡)

## 18. Monotonic Stack

- **Next greater element** — Next larger to the right → Daily Temperatures (LC 739 🟡)
- **Histogram area** — Largest rectangle in histogram → Largest Rectangle in Histogram (LC 84 🔴)
- **Rain water (stack variant)** — Trapped water via stack → Trapping Rain Water (LC 42 🔴)
- **Remove to keep monotonic** — Smallest number after k removals → Remove K Digits (LC 402 🟡)
- **Span / stock** — Consecutive days ≤ today → Online Stock Span (LC 901 🟡)

## 19. Prefix Sum / Hashing

- **Subarray sum = k** — Count subarrays summing to k → Subarray Sum Equals K (LC 560 🟡)
- **Range sum query** — Immutable range sums → Range Sum Query - Immutable (LC 303 🟢)
- **2D prefix** — Region sum in matrix → Range Sum Query 2D (LC 304 🟡)
- **Prefix + divisibility** — Continuous subarray multiple of k → Continuous Subarray Sum (LC 523 🟡)
- **Product except self** — Prefix/suffix products → Product of Array Except Self (LC 238 🟡)

## 20. Bit Manipulation

- **XOR single number** — Element appearing once → Single Number (LC 136 🟢)
- **Bit counting** — 1-bits for 0..n → Counting Bits (LC 338 🟢)
- **Missing via XOR** — Missing number → Missing Number (LC 268 🟢)
- **Bitmask subsets** — Enumerate subsets via bits → Subsets (LC 78 🟡)
- **Sum without +** — Add using bit ops → Sum of Two Integers (LC 371 🟡)

## 21. Trie (Prefix Tree)

- **Basic trie** — Insert/search/prefix → Implement Trie (LC 208 🟡)
- **Wildcard search** — Support '.' matching → Add and Search Word (LC 211 🟡)
- **Trie + backtracking** — Find all words in board → Word Search II (LC 212 🔴)
- **Max XOR pair** — Maximize XOR of two numbers → Maximum XOR of Two Numbers (LC 421 🟡)
- **Autocomplete / search system** — Ranked suggestions → Design Search Autocomplete System (LC 642 🔴)

## 22. Matrix Manipulation

- **In-place rotate** — Rotate image 90° → Rotate Image (LC 48 🟡)
- **Spiral traversal** — Read matrix in spiral → Spiral Matrix (LC 54 🟡)
- **Set zeroes in place** — Zero out rows/cols → Set Matrix Zeroes (LC 73 🟡)
- **Game of life** — In-place next state → Game of Life (LC 289 🟡)

## 23. Design / Data-Structure Implementation

- **LRU cache** — O(1) get/put eviction → LRU Cache (LC 146 🟡)
- **LFU cache** — Frequency-based eviction → LFU Cache (LC 460 🔴)
- **Randomized set** — O(1) insert/remove/getRandom → Insert Delete GetRandom O(1) (LC 380 🟡)
- **Min stack** — O(1) min retrieval → Min Stack (LC 155 🟡)
- **Iterator design** — Flatten nested list → Flatten Nested List Iterator (LC 341 🟡)
- **Rate limiter / hit counter** — Count hits in window → Design Hit Counter (LC 362 🟡)
- **Tweet timeline** — Merge k feeds → Design Twitter (LC 355 🟡)
- **Snapshot array** — Versioned get/set → Snapshot Array (LC 1146 🟡)
- **Skiplist / add-search** — TinyURL / codec → Encode and Decode TinyURL (LC 535 🟡)

## 24. Stacks & Queues (Non-monotonic)

- **Balanced brackets** — Valid parentheses → Valid Parentheses (LC 20 🟢)
- **Expression eval** — RPN evaluation → Evaluate Reverse Polish Notation (LC 150 🟡)
- **Decode nested** — Decode string with counts → Decode String (LC 394 🟡)
- **Queue via stacks / vice-versa** — Implement one with the other → Implement Queue using Stacks (LC 232 🟢)
- **Basic calculator** — Evaluate expression with +,-,(),→ Basic Calculator (LC 224 🔴)

---

## How to use this for a Senior SWE loop

Senior loops lean **medium→hard** and reward pattern recognition + clean, complexity-aware code over exotic algorithms. Priority tiers if time is short:

1. **Highest ROI:** Two Pointers, Sliding Window, Binary Search (esp. search-on-answer), Trees DFS/BFS, Graphs (BFS/DFS + Union-Find + Topo Sort), DP (knapsack, LIS, LCS, grid, decision).
2. **Frequent design ask (senior-specific):** LRU/LFU, Min Stack, Randomized Set, iterators, rate limiters — often paired with concurrency/thread-safety follow-ups.
3. **Rounding out:** Heaps/Top-K, Monotonic Stack, Trie, Backtracking, Prefix Sum, Bit Manipulation.

Tip: for each pattern, be able to state the **trigger** ("sorted array + pair" → two pointers; "contiguous subarray/substring optimum" → sliding window; "min/max under a monotonic constraint" → binary search on answer) and the **time/space** cost out loud.