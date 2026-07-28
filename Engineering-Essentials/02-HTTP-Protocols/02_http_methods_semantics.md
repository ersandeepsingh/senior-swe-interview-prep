# HTTP Methods & Semantics

> Methods aren’t just labels — they carry promises: **safe** (no state change) and **idempotent** (same effect if repeated).

## Plain English

Verbs tell clients, caches, and proxies what is allowed. Misusing them breaks retries and CDN caching. Seniors connect methods to **safe retries**.

## Essentials (must-know for this topic)

### Safe vs idempotent

| Method | Typical use | **Safe?** | **Idempotent?** |
|--------|-------------|-----------|-----------------|
| **GET** | Read | Yes | Yes |
| **HEAD** | Headers only | Yes | Yes |
| **OPTIONS** | CORS / allowed methods | Yes | Yes |
| **PUT** | Replace whole resource | No | Yes |
| **DELETE** | Remove | No | Yes |
| **POST** | Create / trigger action | No | **No** (usually) |
| **PATCH** | Partial update | No | Often yes if carefully designed |

**Safe** = does not change server state. **Idempotent** = N identical requests → same final state.

### PUT vs PATCH vs POST

| Verb | Body meaning | Create? |
|------|--------------|---------|
| **POST** `/orders` | New subordinate / process | Server assigns id → `201` |
| **PUT** `/orders/42` | **Full** representation | Create-or-replace if client picks id |
| **PATCH** `/orders/42` | **Partial** diff | Update only sent fields |

### Retry implication (interview gold)

| Method | Retry freely? |
|--------|----------------|
| GET / PUT / DELETE | Yes (idempotent) |
| POST | Only with **Idempotency-Key** (or equivalent) |
| PATCH | Yes if patch application is idempotent |

## Why seniors get asked

Idempotency and verb misuse show up in API design and retry logic. Seniors connect methods to safe retries and caching.

## Simple example

```http
GET    /orders/42          → read
POST   /orders             → create (new id)
PUT    /orders/42          → replace entire order
PATCH  /orders/42          → {"status":"cancelled"}
DELETE /orders/42          → remove
```

```bash
curl -X PATCH https://api.example.com/orders/42 \
  -H "Content-Type: application/json" \
  -d '{"status":"cancelled"}'
```

## When to use / when not / trade-offs

| Prefer | When |
|--------|------|
| GET | Cacheable reads, CDNs |
| PUT | Client knows the id; full replace |
| PATCH | Sparse updates; large resources |
| POST | Server assigns id; non-idempotent actions |

**Trade-off:** overloading POST for everything is easy but breaks caches and retry assumptions.

## Common pitfalls

- GET with side effects (logging “read” is fine; charging a card is not)
- Using PUT for partial updates (accidentally nulling omitted fields)
- Retrying POST without idempotency keys → duplicate charges
- Ignoring that DELETE is idempotent (second delete → 404 is OK)

## Interview trigger phrase

> “GET is safe; PUT/DELETE are idempotent; POST needs an idempotency key if clients may retry.”

## Exercise

Payment capture can be retried by the client. Choose method + path + one header so a double-submit doesn’t charge twice. Explain PUT vs POST for this case.
