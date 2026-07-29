# Handling Millions of Requests Efficiently

> **One-line definition:** Serving LLM traffic at scale means absorbing bursty demand behind queues and async workers, spreading load across provider capacity within their rate limits, and degrading gracefully when the model tier is the bottleneck — not your CPU.

---

## Plain English

A normal web service scales by adding stateless replicas: more pods, more throughput. LLM services **don't** scale that way, because the slow, expensive, rate-limited part lives at the **provider**, not in your process. Your worker spends 2–20 seconds mostly *waiting* on the model.

So the game changes:

- Your machines are cheap and fast; the **model is the scarce resource**.
- The provider enforces hard ceilings: **RPM** (requests/min) and **TPM** (tokens/min). Blow past them and you get `429 Too Many Requests`.
- One request can cost 100× more tokens than another, so "requests per second" is a lie — you must think in **tokens per second**.

The winning architecture: accept requests instantly, **queue** the work, let a **pool of async workers** drain the queue at a rate the provider allows, and stream partial results back so users don't stare at a spinner. When you can't keep up, you shed or downgrade load on purpose instead of falling over.

Remember the mental model from earlier modules: the **model is an untrusted probabilistic planner**, your **APIs are the trusted executor**. At scale this matters twice — a retry storm or a runaway agent loop can multiply both your bill and your side effects.

---

## Essentials

### The two limits that actually bind you

| Limit | Unit | Who sets it | What blowing it looks like | How you stay under it |
|-------|------|-------------|----------------------------|-----------------------|
| **RPM** | requests / minute | Provider (per key/org) | HTTP `429`, `retry-after` header | Throttle in-flight requests, one queue drain rate |
| **TPM** | tokens / minute (in + out) | Provider (per key/org) | HTTP `429` even at low RPM | Estimate tokens *before* sending; budget by tokens |
| **Concurrency** | in-flight requests | You + provider | timeouts, memory blowup | Bounded worker pool / semaphore |
| **Context window** | tokens / request | Model | truncation, `400` | Trim/summarize context (see cost module) |

> Track a **token budget per minute**, not a request count. A single request can be 50 tokens or 50k.

### Core scaling building blocks

| Building block | Problem it solves | Cost / trade-off |
|----------------|-------------------|------------------|
| **Queue** (SQS/Kafka/Redis) | Burst absorption, smoothing | Adds latency; needs a job store |
| **Async workers** | High concurrency without threads-per-request | Harder debugging, need backpressure |
| **Backpressure** | Stops the queue from growing forever | Must reject/slow producers |
| **Load balancing across providers/models** | More total TPM, resilience to one provider's outage/429s | Output drift between models, more keys to manage |
| **Autoscaling workers** | Match worker count to demand | Scaling on the *wrong* signal (CPU) is useless |
| **Batching** | Amortize overhead (esp. embeddings) | Adds wait; only some endpoints support it |
| **Streaming** | Perceived latency, early cancel | More connection state, partial-output handling |
| **Graceful degradation** | Stay up under overload | Users get a worse (but real) answer |

### Sync vs async request handling

| Aspect | Synchronous (request → wait → respond) | Async (enqueue → worker → callback/poll/stream) |
|--------|----------------------------------------|-------------------------------------------------|
| Good for | Low volume, simple chat | High volume, spiky, long jobs |
| Burst behavior | Falls over / times out | Absorbs into queue |
| Client model | Blocks | Polls, websocket, or SSE stream |
| Failure isolation | One bad request ties a thread | Retriable job, isolated |

### Autoscaling: scale on the right signal

CPU stays near-idle while workers wait on the network, so **CPU-based autoscaling never triggers** and you under-provision. Scale on:

| Signal | Why it's better |
|--------|-----------------|
| **Queue depth / age of oldest job** | Directly measures backlog |
| **In-flight requests to provider** | Tracks the real bottleneck |
| **Token throughput vs TPM budget** | Tells you if adding workers even helps (it won't if you're TPM-capped) |

> If you're **TPM-capped**, adding workers does nothing but generate more `429`s. Add provider capacity or shed load instead.

### Batching vs streaming (they solve different things)

- **Batching** = throughput. Send many inputs in one call (embeddings, classifications) to cut per-call overhead and cost.
- **Streaming** = latency *perception*. Tokens arrive as generated, so time-to-first-token is ~200ms even if the full answer takes 8s. Also lets you cancel early and stop paying for output.

---

## Architecture diagram

```text
                         ┌──────────────────────────────────────────────┐
   millions of clients   │                 YOUR SYSTEM                   │
   ───────────────────►  │                                              │
                         │  ┌──────────┐   enqueue   ┌───────────────┐  │
   HTTP / websocket ────►│  │  API /   │────────────►│    QUEUE      │  │
                         │  │ Gateway  │             │ (SQS/Kafka)   │  │
   (accepts instantly)   │  │  + auth  │◄──── ack ───│  jobs waiting │  │
                         │  └────┬─────┘             └──────┬────────┘  │
                         │       │ stream back              │ pull      │
                         │       ▼                          ▼           │
                         │  ┌──────────┐            ┌─────────────────┐ │
                         │  │ SSE /    │            │  WORKER POOL    │ │
                         │  │ WS out   │◄───────────│ (async, bounded │ │
                         │  └──────────┘   tokens   │  concurrency,   │ │
                         │                          │  backpressure)  │ │
                         │                          └───┬────────┬────┘ │
                         └──────────────────────────────┼────────┼──────┘
                              rate limiter / token       │        │
                              budget per provider ───────┤        │
                                                         ▼        ▼
                                              ┌──────────────┐  ┌──────────────┐
                                              │ Provider A    │  │ Provider B   │
                                              │ (primary,     │  │ (fallback /  │
                                              │  RPM/TPM cap) │  │  overflow)   │
                                              └──────────────┘  └──────────────┘
```

- **Gateway** authenticates, applies per-tenant quotas, enqueues, returns a job/stream handle instantly.
- **Queue** absorbs bursts so a 10× spike becomes a longer wait, not a crash.
- **Workers** drain at a rate the **rate limiter** allows (token-budget aware), fan out across providers.
- **Provider B** soaks overflow or takes over when A returns `429`/5xx.

---

## Concrete example: a token-aware worker loop

```python
# Pseudocode. Bounded concurrency + token budget + backpressure.
sem = Semaphore(MAX_INFLIGHT)          # concurrency cap
token_bucket = TokenBucket(tpm=200_000)  # refill 200k tokens/min

async def worker(queue):
    while True:
        job = await queue.pull()        # blocks if empty (no busy loop)
        est_tokens = estimate_tokens(job.prompt) + job.max_output
        await token_bucket.take(est_tokens)   # backpressure: wait for budget
        async with sem:                        # backpressure: cap in-flight
            try:
                async for chunk in provider.stream(job.prompt):
                    await job.stream_out(chunk)   # streaming UX
            except RateLimited as e:
                await queue.requeue(job, delay=e.retry_after)  # respect 429
            except ProviderDown:
                await fallback_provider.handle(job)  # load-balance away
```

Key points: the model call is the only slow part, so everything is `async`; the **token bucket + semaphore** are your backpressure valves; `429` re-queues instead of hammering.

---

## When to use / trade-offs

| Situation | Do this |
|-----------|---------|
| Low, steady traffic | Simple synchronous calls + basic retry. Don't over-build. |
| Spiky / high volume | Queue + async workers + streaming. |
| Latency-sensitive UX | Stream tokens; show partial output; consider a smaller/faster model. |
| Cost-sensitive bulk jobs | Batch, cache, use cheaper models, off-peak processing. |
| Hard TPM ceiling | Multi-provider/multi-key load balancing; negotiate higher limits. |

Trade-offs: queues add latency and operational surface; multi-provider adds output inconsistency; streaming complicates error handling (you may have already sent half an answer when it fails).

---

## Pitfalls

- **Scaling on CPU.** Workers are I/O-bound; CPU stays idle. Scale on queue depth / token throughput.
- **Counting requests, not tokens.** One request ≠ one unit of load. Budget by TPM.
- **Retry storms.** A provider blip → everyone retries → self-inflicted `429` flood. Use backoff + jitter + a circuit breaker.
- **Unbounded concurrency.** No semaphore → you melt the provider's limit and your own memory.
- **Ignoring `retry-after`.** The provider tells you exactly how long to wait; honor it.
- **Runaway agent loops at scale.** A tool-calling loop that doesn't terminate multiplies cost and real side effects across millions of sessions. Cap steps.
- **Streaming without cancel.** User closes the tab, you keep paying for tokens. Wire cancellation to the stream.

---

## Interview trigger phrase

> "I scale on tokens, not requests. Clients hit a gateway that enqueues instantly; a bounded pool of async workers drains the queue under a per-minute token budget, load-balances across providers, and streams tokens back. When I'm TPM-capped I shed or downgrade load — adding workers just manufactures 429s."

---

## Exercise

Your support chatbot normally does 50 requests/sec, but a product outage causes a 20× spike. Your provider allows 500 RPM and 300k TPM on your key.

1. At 1000 req/sec incoming, what happens if you call the provider synchronously with no queue? What HTTP error dominates?
2. Design the flow so users still get *something*. Where does the queue go, and what do you tell users waiting in it?
3. You add 5× more workers and it doesn't help — latency stays flat. What limit are you almost certainly hitting, and what are your two real options?
