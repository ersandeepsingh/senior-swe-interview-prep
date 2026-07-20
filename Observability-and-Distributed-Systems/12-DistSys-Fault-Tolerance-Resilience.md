# 12 · Distributed Systems — Fault Tolerance & Resilience

> Staying up (or degrading gracefully) when parts inevitably fail.

---

## Failure detection

**Definition:** Mechanisms for deciding a node is dead: heartbeats, gossip, phi-accrual detectors, and timeouts.

**Simple explanation:** You can't directly know if a remote node crashed or is just slow/unreachable — you infer it. **Heartbeats:** nodes periodically ping; missed pings ⇒ suspected dead. **Gossip:** nodes share health info peer-to-peer so the whole cluster converges on who's alive. **Phi-accrual:** outputs a *suspicion level* instead of a binary dead/alive, adapting to network conditions.

**Example:** In Cassandra, nodes gossip every second. If Node C's heartbeat isn't seen and the phi-accrual detector's suspicion crosses a threshold, peers mark C down and stop routing to it — while tolerating brief network blips without over-reacting.

---

## Retries with backoff + jitter

**Definition:** Re-attempting a failed operation, waiting progressively longer between tries (exponential backoff) with added randomness (jitter).

**Simple explanation:** Naive immediate retries can hammer a struggling service and cause a **retry storm** (a self-inflicted DDoS). Exponential backoff spaces retries out (1s, 2s, 4s...). Jitter randomizes the delay so thousands of clients don't retry in lockstep and create synchronized spikes. Always cap retries and only retry idempotent/safe operations.

**Example:** A call fails. Retry after `random(0, 1s)`, then `random(0, 2s)`, then `random(0, 4s)`, giving up after 3 tries. Without jitter, 10,000 clients would all retry at exactly 1s, 2s, 4s — re-crashing the recovering service each time.

---

## Circuit breaker

**Definition:** A pattern that stops calling a failing dependency after errors cross a threshold, "opening" to fail fast, then testing recovery before "closing" again.

**Simple explanation:** Like an electrical breaker. **Closed** = calls flow normally. Too many failures → **Open** = calls fail instantly (don't even try), giving the dependency room to recover and freeing your threads. After a cooldown → **Half-open** = allow a few trial calls; if they succeed, close; if not, re-open. Prevents one sick service from dragging down callers.

**Example:** The payment service starts timing out. After 50% of calls fail in a window, the breaker opens: for the next 30s, checkout instantly returns "payment unavailable, try later" instead of hanging 10s per request. After 30s it lets one request through to test if payment recovered.

---

## Bulkhead & isolation

**Definition:** Partitioning resources (thread pools, connection pools) so a failure in one area can't consume all resources and sink the whole system.

**Simple explanation:** Named after ship compartments that keep one flooded section from sinking the vessel. You give each dependency its own resource pool, so if one gets slow and saturates *its* pool, other features keep working with *their* pools intact.

**Example:** A service uses separate thread pools for `payments` (10 threads) and `recommendations` (10 threads). Recommendations hangs and exhausts its 10 threads — but checkout still works because payments has its own untouched pool. Without bulkheads, the hang would eat *all* threads and take everything down.

---

## Timeouts & deadlines

**Definition:** Bounding how long you'll wait for an operation, and propagating a shared deadline through a call chain.

**Simple explanation:** Without timeouts, one slow dependency ties up your threads/connections until they're exhausted (cascading failure). A **deadline** is even better: the client sets "this whole request must finish by T," and every downstream service respects the remaining time — so nobody keeps working on a request the caller already gave up on.

**Example:** Client sets a 2s deadline. Gateway spends 500ms, then calls the order service passing "1.5s remaining." The order service calls the DB with a timeout of the remaining budget. If time runs out anywhere, everyone stops immediately rather than doing doomed work.

---

## Graceful degradation

**Definition:** Continuing to provide reduced but useful functionality when some components fail, instead of failing completely.

**Simple explanation:** A partial experience beats an error page. When a non-critical dependency is down, serve a fallback: cached/stale data, a default, or a hidden feature — while keeping the core path working.

**Example:** The recommendation service is down. Instead of erroring the whole homepage, the site shows a generic "popular items" list (a cached fallback). Users barely notice, and the critical browse/checkout flows are unaffected.

---

## Redundancy & failover

**Definition:** Running spare capacity so that when a component dies, another takes over. **Active-active** = all instances serve traffic; **active-passive** = a standby waits to be promoted.

**Simple explanation:** No single instance should be a single point of failure. Active-active uses all nodes (better utilization, instant failover) but needs conflict handling. Active-passive keeps a warm standby that's promoted on failure (simpler, but the standby's capacity sits idle and failover takes a moment).

**Example:**
- **Active-active:** two regions both serve users behind a load balancer; if one region dies, the other absorbs all traffic instantly.
- **Active-passive:** a primary DB with a standby replica; if the primary fails, the standby is promoted to primary (a few seconds of failover).

---

## Rate limiting & load shedding

**Definition:** **Rate limiting** caps how many requests a client/system may make; **load shedding** deliberately drops lower-priority work when overloaded to protect the system.

**Simple explanation:** Rate limiting enforces fairness and blocks abuse ("100 req/min per user"). Load shedding is triage under overload: when you can't serve everyone, drop or reject low-value requests so high-value ones (and the system itself) survive, rather than collapsing entirely.

**Example:** Rate limit: an API returns `429 Too Many Requests` to a client exceeding its quota. Load shedding: during a traffic spike, the service rejects non-critical background/analytics requests with `503` so that checkout requests still get served.

---

## Chaos engineering

**Definition:** Deliberately injecting failures into production (or prod-like) systems to verify they tolerate them.

**Simple explanation:** You don't truly know your failover works until it's tested for real. Chaos engineering intentionally kills instances, adds latency, or severs network links to expose weaknesses *before* a real outage does — on your terms, with a blast-radius limit and a hypothesis.

**Example:** Netflix's Chaos Monkey randomly terminates production instances during business hours. If killing an instance ever causes user-visible impact, that's a resilience bug to fix — better discovered deliberately at 2pm than by accident at 2am.
