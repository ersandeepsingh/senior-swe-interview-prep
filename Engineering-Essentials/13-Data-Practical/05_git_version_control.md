# Git & Version Control

> The daily tool for collaboration. Seniors know **branching, history hygiene, and PR workflow** — not just `commit -m "fix"`.

## Plain English

**Git** stores snapshots + history. Prefer short-lived branches, small PRs, and CI gates. Don't rewrite shared `main`.

```text
  main ─●─●─●──────────●
           \           /
            ●─●─● (feature, PR merged)
```

## Essentials (must-know for this topic)

### Core habits

| Habit | Why |
|-------|-----|
| Small commits | Easy review/revert |
| Feature branches | Isolate work |
| Pull requests | Review, CI gate |
| Meaningful messages | Future archaeology |
| Don't rewrite shared history casually | Protect teammates |

### Branching models

| Model | Idea | Fit |
|-------|------|-----|
| **Trunk-based** | Short-lived branches; merge to `main` often; flags for incomplete work | Most SaaS |
| **GitFlow** | `develop` + long-lived `release`/`hotfix` | Versioned packaged software; often overkill for SaaS |

### Merge vs rebase

| | **Merge** | **Rebase** |
|---|-----------|------------|
| History | Preserves exact branch topology; merge commits | Replays commits → linear history |
| Safe on shared branches? | Yes | **No** (unless team agrees + force-push policy) |
| Typical use | Merge PR to main | Clean up **your** feature branch onto latest main |

### PR hygiene (senior signal)

| Do | Don't |
|----|-------|
| Small, reviewable PRs | Huge mixed formatting + logic PRs |
| CI green before merge | Force-push to `main` |
| Revert on shared history | Rewrite history to hide mistakes |
| Secret scanning / never commit secrets | Commit `.env` “temporarily” |

## Simple example

Good flow:

1. `git checkout -b feat/idempotency-key`
2. Commit logically: “add idempotency store”, “wire payment handler”, “tests”.
3. Push, open PR, CI green, address review.
4. Squash or rebase per team norm; merge to `main`.
5. Deploy from `main` (or release tag).

Conflict: rebase onto latest `main`, fix conflicts, force-push **your feature branch only** if that's team policy.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Trunk-based + flags | Fast integration | Need flag discipline |
| Long-lived branches | Isolation | Painful merges, drift |
| Squash merge | Clean main | Lose fine-grained commit history |
| Rebase culture | Linear history | Steeper learning; force-push risks |

## Pitfalls

- **Committing secrets** — rotate immediately; use pre-commit scanners.
- **Force-push to `main`**.
- **Huge PRs** nobody can review.
- **“Fix” commits that mix formatting + logic**.
- **Rewriting history to hide mistakes** instead of revert commits on shared branches.

## Interview trigger phrase

> “I prefer **short-lived branches**, **small PRs** gated by CI, and **trunk-based** development with feature flags — rebase locally for clarity, but I don't rewrite shared `main`.”

## Exercise

Your feature branch is 10 commits behind `main` with conflicts in one file. List the commands/steps you'd use without destroying teammates' clones of `main`.
