# Status Codes

> A three-digit code that tells clients **what happened** so they can retry, redirect, or show an error — without parsing prose.

## Plain English

Status codes are the shared language between APIs, browsers, LBs, and monitors. Correct codes make retries and alerts behave; `200` for every error is a classic junior smell.

## Essentials (must-know for this topic)

### Classes (grouped meanings)

| Class | Meaning | Client action |
|-------|---------|---------------|
| **1xx** | Informational | Rare in app APIs |
| **2xx** | Success | Proceed |
| **3xx** | Redirect / cache validation | Follow Location or use cached |
| **4xx** | Client fault | Fix request; usually **don’t** blind-retry |
| **5xx** | Server / upstream fault | May retry with backoff |

### Codes you’ll actually use

| Code | Meaning |
|------|---------|
| `200` | OK (body) |
| `201` | Created (`Location` often set) |
| `204` | Success, **no body** (common for DELETE) |
| `301` / `302` / `307` | Permanent / temporary redirect (`307` keeps method) |
| `304` | Not Modified (conditional GET) |
| `400` | Bad request / validation |
| `401` | **Unauthenticated** (“who are you?”) |
| `403` | **Forbidden** (“I know you; not allowed”) |
| `404` | Missing |
| `409` | Conflict (duplicate, version, state machine) |
| `422` | Semantically invalid but well-formed (common in APIs) |
| `429` | Rate limited → honor `Retry-After` |
| `500` | Bug / unexpected |
| `502` | Bad gateway (upstream bogus) |
| `503` | Unavailable → often retryable |
| `504` | Gateway timeout |

### Retry cheat sheet

| Code | Retry? |
|------|--------|
| `429`, `503` | Yes — respect `Retry-After` |
| `500`, `502`, `504` | Maybe — bounded backoff |
| `400`, `401`, `403`, `404` | No (fix the request/auth) |

**401 vs 403:** not logged in vs logged in but not permitted.

## Why seniors get asked

Correct codes make load balancers, clients, and monitors behave. Misusing `200` for errors is a classic junior smell.

## Simple example

```http
HTTP/1.1 201 Created
Location: /orders/43

HTTP/1.1 429 Too Many Requests
Retry-After: 30

HTTP/1.1 503 Service Unavailable
Retry-After: 120
```

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://api.example.com/orders/999
# 404
```

## When to use / when not / trade-offs

| Code | Use when |
|------|----------|
| 401 vs 403 | 401 = “who are you?”; 403 = “I know you, you’re not allowed” |
| 404 vs 403 | Sometimes hide existence (return 404 for private resources) |
| 409 | Version conflict / state machine violation |
| 422 | Semantically invalid but well-formed (common in APIs) |

**Trade-off:** hyper-precise codes help clients; inconsistent use across services confuses everyone — pick a house style.

## Common pitfalls

- Always `200` + `{"success":false}`
- `401` when the user is logged in but lacks permission (should be `403`)
- Retrying `400` in a loop
- Using `500` for “user not found”

## Interview trigger phrase

> “I’d return 429/503 with Retry-After for throttling and overload, and never hide application errors behind a blanket 200.”

## Exercise

Map these to status codes: duplicate email on signup; valid token but not admin; rate limit exceeded; dependency down; successful delete with empty body.
