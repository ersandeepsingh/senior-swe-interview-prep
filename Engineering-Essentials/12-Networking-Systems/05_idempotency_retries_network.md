# Idempotency & Retries at the Network Layer

> The network is a liar: you may get **timeouts after the server already succeeded**. Retries without idempotency cause duplicates; no retries cause user pain.

## Plain English

Classic failure modes:

1. Request lost → safe to retry.
2. Response lost after server committed → retry looks like a duplicate.
3. LB kills idle connection → client sees error mid-flight.

So clients and proxies **must** assume at-least-once. Make writes safe with **idempotency keys**, **safe HTTP methods**, or **dedupe** on the server.

```text
  Client                Server
    |-- POST /charge -->|
    |                   |-- charge OK (committed)
    | X-- timeout ------|   (response lost)
    |-- POST /charge -->|  without key → DOUBLE CHARGE
    |-- POST + same key→|  with key → return first result
```

## Essentials (must-know for this topic)

### Timeout ≠ failure (unknown outcome)

| What client sees | What may have happened |
|------------------|------------------------|
| Timeout / connection reset | Never reached server **or** succeeded and response lost |
| Safe stance | Treat as **unknown** → reconcile or retry **idempotently** |

### What is safe to retry

| Safe-ish | Dangerous without design |
|----------|--------------------------|
| **GET**, **PUT**, **DELETE** (idempotent methods) | Blind **POST** retries |
| POST **with same idempotency key** | New key on every attempt |
| Transient 503 / network errors | 400 / 401 / 403 retries |

### Retry alignment rules

| Rule | Why |
|------|-----|
| **One** retry layer (usually app client) | Gateway + client + SDK all retry → amplification |
| Backoff + **jitter** | Avoid synchronized stampede |
| Prefer **status lookup** after ambiguous success | Better than blind duplicate POST |
| TCP retransmit ≠ app retry | TCP fixes packets *within* a connection; timeouts need app-level policy |

## Simple example

Mobile checkout:

1. Generate `idempotency_key` once per user intent (button press).
2. POST with that key; on timeout/5xx, retry same key with backoff+jitter.
3. Server stores key → payment_id; repeats return same payment_id.
4. Don't generate a **new** key on retry — that defeats the purpose.

TCP retransmits handle packet loss *within* a connection; they don't replace application-level retries across **new** connections after a timeout.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Automatic HTTP retries at proxy | Masks blips | Duplicate POSTs if not careful |
| App-level idempotent retries | Correctness | Need key store / design |
| Fail fast, no retries | Simple | Worse UX on blips |
| Long client timeouts | Fewer false timeouts | Slow failure, resource hold |

## Pitfalls

- **Retrying on 400/401/403** — won't help; fix the request.
- **New idempotency key every attempt**.
- **Retry amplification** through multiple hops.
- **Assuming TCP reliability = exactly-once business ops**.
- **Ignoring “success ambiguous”** after timeout — must reconcile via GET/status API.

## Interview trigger phrase

> “On timeout I'd treat the outcome as **unknown**, retry only with an **idempotency key**, and prefer a **status lookup** over blind duplicate POSTs.”

## Exercise

Payment POST times out. Write the client algorithm for: first attempt, timeout, retry, and how you detect the charge already existed.
