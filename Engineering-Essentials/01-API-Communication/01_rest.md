# REST

> Represent resources with URLs; change them with HTTP verbs; keep the server **stateless** between requests.

## Plain English

Think of your API as a filing cabinet. Each folder is a **resource** (`/orders/42`). You use HTTP verbs to act on it. The server does not remember “who you are mid-conversation” beyond what you send (token, cookie) — every request stands alone.

## Essentials (must-know for this topic)

### HTTP verbs — what they mean & how they differ

| Verb | Intent | Body? | Typical success | Safe? | Idempotent? |
|------|--------|-------|-----------------|-------|-------------|
| **GET** | Read a resource | No | `200` | Yes | Yes |
| **POST** | Create / trigger an action | Yes | `201` (create) or `200`/`202` | No | **No** (unless you add an idempotency key) |
| **PUT** | Replace the whole resource | Yes | `200` / `204` | No | Yes |
| **PATCH** | Partial update | Yes | `200` / `204` | No | Usually yes if applied carefully |
| **DELETE** | Remove | Optional | `200` / `204` | No | Yes (repeat delete → same end state) |
| **HEAD** | Like GET, headers only | No | `200` | Yes | Yes |
| **OPTIONS** | What methods/CORS allow | No | `200` / `204` | Yes | Yes |

**Safe** = does not change server state. **Idempotent** = same request N times → same final state.

**PUT vs PATCH (quick):**
- `PUT /users/1` with full body → replace entire user
- `PATCH /users/1` with `{ "email": "x@y.com" }` → change only email

**POST vs PUT for create:**
- `POST /orders` → server assigns id → `201` + `Location`
- `PUT /orders/42` → client picks id; create-or-replace

### Core REST ideas that belong here

| Idea | Meaning |
|------|---------|
| **Resource** | Noun in the URL (`/orders`, `/orders/42`) — not a verb (`/createOrder`) |
| **Stateless** | Each request carries auth + data; no server “conversation memory” |
| **Uniform interface** | Same verbs/status semantics everywhere |
| **Representation** | JSON (or XML) of the resource, not the DB row itself |
| **HATEOAS** (optional) | Response includes links to next actions — rarely required in interviews beyond naming it |

### Status codes you’ll use with REST

| Code | When |
|------|------|
| `200` | OK (read/update) |
| `201` | Created |
| `204` | Success, no body |
| `400` | Bad request / validation |
| `401` | Not authenticated |
| `403` | Authenticated but not allowed |
| `404` | Resource missing |
| `409` | Conflict (e.g. duplicate) |
| `429` | Rate limited |
| `500` / `503` | Server / unavailable |

## Why seniors get asked

REST is the default public API style. Seniors must explain resources vs RPC-style endpoints, verb semantics, status codes, and why “stateless” helps horizontal scaling.

## Simple example

```http
GET /api/v1/orders/42 HTTP/1.1
Authorization: Bearer eyJ...
Accept: application/json

HTTP/1.1 200 OK
Content-Type: application/json

{"id":"42","status":"shipped","total_cents":1999}
```

```http
POST /api/v1/orders HTTP/1.1
Content-Type: application/json
Idempotency-Key: 7f3a-...

{"items":[{"sku":"TSHIRT","qty":2}]}

HTTP/1.1 201 Created
Location: /api/v1/orders/43
```

## When to use / when not / trade-offs

| Use REST when… | Prefer something else when… |
|----------------|-----------------------------|
| Public HTTP APIs, CRUD-shaped domains | Mobile needs many shapes of the same data → GraphQL |
| Caching, CDNs, standard tooling matter | Internal service-to-service, strict contracts → gRPC |
| Team already thinks in resources | True bidirectional realtime → WebSockets |

**Trade-off:** simple and universal, but clients often over-fetch or under-fetch; many round trips for nested data.

## Common pitfalls

- RPC-flavored URLs (`POST /getUser`) that ignore HTTP semantics
- Using `200` for every error with a body message (breaks proxies and clients)
- Using `PUT` when you meant partial update (`PATCH`), or `POST` for everything
- Forgetting idempotency on payment/create endpoints
- Putting session state on the server and calling it “REST”

## Interview trigger phrase

> “I’d model orders as resources, pick verbs by semantics (GET read, POST create, PUT replace, PATCH partial), keep handlers stateless, and make create safe to retry with an idempotency key.”

## Exercise

Design three endpoints for a blog: list posts, get one post, create a comment. For each, name the method, path, success status, and whether it is idempotent. Say one thing you would *not* put in the URL.
