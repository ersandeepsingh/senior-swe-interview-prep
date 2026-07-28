# API Contracts & Versioning

> An API is a **promise**. Versioning and compatibility rules let producers evolve without breaking consumers — and vice versa.

## Plain English

A **contract** is the agreed shape: paths, fields, types, errors, auth. Prefer explicit schemas (OpenAPI, Protobuf, GraphQL SDL) over tribal knowledge.

```text
  Safe:    add optional `nickname`
  Risky:   rename `name` → `full_name` (break old clients)
  Safer:   add `full_name`, keep `name` deprecated for 2 quarters
```

For mobile apps that update slowly: support **N and N-1** (sometimes N-2) for months.

## Essentials (must-know for this topic)

### Compatibility vocabulary

| Term | Meaning |
|------|---------|
| **Backward compatible** | Old clients still work (add optional field) |
| **Forward compatible** | New clients tolerate older servers (ignore unknown fields) |
| **Breaking change** | Remove/rename required field, change meaning, tighten validation |

### Versioning strategies

| Approach | Example | Notes |
|----------|---------|-------|
| **URL version** | `/v1/orders` | Explicit, easy to route; versions linger |
| **Header version** | `Accept: application/vnd.myapp.v2+json` | Cleaner URLs; harder to discover |
| **Additive evolution** | No bump; only compatible changes | Best default for internal APIs |

### Safe vs breaking changes

| Usually safe | Usually breaking |
|--------------|------------------|
| Add optional field | Remove / rename field |
| Add new endpoint | Change field type or meaning |
| Relax validation | Make optional field required |
| Deprecate with sunset date | Silent semantic change (same name, new meaning) |

**Contract tests (consumer-driven):** catch breaks in CI before prod.

## Simple example

Shipping `v1` response:

```json
{ "order_id": "o1", "status": "paid" }
```

Compatible `v1` evolution:

```json
{ "order_id": "o1", "status": "paid", "paid_at": "2026-07-25T10:00:00Z" }
```

Breaking → need `v2` (or careful dual-write period):

```json
{ "id": "o1", "state": "PAID" }
```

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Strict semantic versioning in URL | Clear break points | Many parallel versions to maintain |
| Compatibility-only evolution | Less version sprawl | Discipline; hard for big redesigns |
| Contract tests (consumer-driven) | Catch breaks in CI | Upfront investment |
| “We'll just tell clients to update” | Fast for producer | Outages for slow consumers |

## Pitfalls

- **Silent meaning changes** — same field, new semantics (status codes that used to mean X now mean Y).
- **No deprecation policy** — v1 lives forever with no sunset date.
- **Versioning everything** including tiny additive changes.
- **Breaking internal APIs casually** because “we own both sides” — until three teams depend on you.

## Interview trigger phrase

> “I'd treat the API as a **compatibility contract** — prefer additive changes, deprecate with a sunset, and only cut a new version for true breaks; consumer-driven contract tests guard CI.”

## Exercise

You must change `amount` from dollars float to integer cents. Propose a zero-downtime migration that keeps old mobile clients working for 90 days.
