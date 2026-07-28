# REST Maturity & Design

> Good REST is versioned, paginated, filterable, and has a clear error contract — not just “JSON over HTTP.”

## Plain English

Anyone can sketch `GET /users`. Production APIs need a maturity level, safe list endpoints, and a contract that survives evolution. Seniors own **versioning**, **pagination**, **filtering/sorting**, and **error shapes** clients can rely on.

## Essentials (must-know for this topic)

### Richardson Maturity Model

| Level | What it means | Reality |
|-------|----------------|---------|
| **0** | Single endpoint, RPC in a POST body | Soap-ish / “JSON-RPC over HTTP” |
| **1** | Resources (`/orders`) | Better URLs, still weak verbs |
| **2** | HTTP verbs + meaningful status codes | **Most production APIs** |
| **3** | HATEOAS — links for next actions | Rare; don’t force it |

### Pagination — pick by list shape

| Style | How | Use when | Avoid when |
|-------|-----|----------|------------|
| **Offset** (`?page=3&limit=20`) | `OFFSET/LIMIT` | Small/stable admin lists | Deep pages on hot tables (`page=5000`) |
| **Cursor** (`?cursor=…&limit=20`) | Opaque key of last row | Infinite scroll, large/changing lists | Need “jump to page 47” |

**Cursor wins** for feeds: stable under inserts, index-friendly (`WHERE (created_at, id) < (?, ?) ORDER BY … LIMIT`).

### Versioning options

| Approach | Example | Pro | Con |
|----------|---------|-----|-----|
| **URL** | `/api/v2/orders` | Obvious in logs/curl | Route duplication |
| **Header** | `Accept: application/vnd.myapp.v2+json` | Cleaner URLs | Harder to debug in browser |
| **Additive only** | New optional fields | No bump needed | Can’t rename/remove freely |

Prefer **backward-compatible additive changes**; bump version only for breaks.

### Error contract (house style)

| Field | Why |
|-------|-----|
| `error.code` | Machine-stable (`ORDER_NOT_FOUND`) |
| `error.message` | Human-readable |
| `request_id` | Support / tracing correlation |

Filter/sort: allowlist fields (`?status=open&sort=-created_at`) — never pass raw column names from clients into SQL.

## Why seniors get asked

Anyone can sketch `GET /users`. Seniors show they’ve shipped APIs that evolve without breaking clients and that handle “list 10 million rows” safely.

## Simple example

```http
GET /api/v2/orders?status=open&limit=20&cursor=eyJpZCI6MTAwfQ
Accept: application/json
```

```json
{
  "data": [{"id": "101", "status": "open"}],
  "paging": {"next_cursor": "eyJpZCI6MTAxfQ", "has_more": true},
  "error": null
}
```

Error contract (consistent):

```json
{
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "Order 999 does not exist",
    "request_id": "req_abc123"
  }
}
```

## When to use / when not / trade-offs

| Prefer… | Avoid… |
|---------|--------|
| Cursor pagination for large/changing lists | Offset pagination (`page=5000`) on hot tables |
| Additive, backward-compatible changes | Breaking field renames without a version bump |
| Stable machine-readable `error.code` | Free-text-only errors |

**Trade-off:** URL versioning is obvious but duplicates routes; header versioning is cleaner but harder to debug in a browser.

## Common pitfalls

- Breaking clients by renaming JSON fields “just this once”
- Returning unbounded lists
- Mixing 404 “resource missing” with 404 “wrong path” without docs
- Over-engineering HATEOAS when a mobile app hardcodes paths anyway

## Interview trigger phrase

> “I’d ship level-2 REST: resources, verbs, status codes, cursor pagination, and a stable error envelope — version only when we must break.”

## Exercise

A `GET /products` returns 50k rows and clients time out. Propose pagination + filtering. Explain why you’d choose cursor over `offset/limit` for an infinite scroll feed.
