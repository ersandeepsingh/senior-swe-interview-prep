# 06 · Observability — Health, Debugging & Profiling

> Knowing a service is alive, ready, and performing — and digging in when it isn't.

---

## Health checks (liveness vs readiness)

**Definition:** Endpoints an orchestrator polls to decide a service's state. **Liveness** = "is the process alive or stuck?" **Readiness** = "is it ready to receive traffic right now?"

**Simple explanation:** Liveness failing → restart the container. Readiness failing → stop sending it traffic but don't kill it (it may be warming up or a dependency is briefly down). Conflating them causes bad behavior — e.g., killing a pod that's just waiting on a slow dependency.

**Example:**
```
GET /healthz  (liveness)  → 200 if the app loop isn't deadlocked
GET /readyz   (readiness) → 200 only if DB + cache connections are up
```
On startup a pod is *live* but not *ready* until it has warmed its cache and connected to the DB; Kubernetes withholds traffic until `/readyz` returns 200.

---

## Synthetic vs real-user monitoring

**Definition:** **Synthetic** monitoring runs scripted fake requests on a schedule; **real-user monitoring (RUM)** measures actual users' experiences.

**Simple explanation:** Synthetic checks catch problems *before* users do and give consistent baselines (great for uptime probes), but they don't reflect real diversity of devices/networks. RUM shows what users actually experience but only after they hit the problem. Use both.

**Example:**
- **Synthetic:** every 60s, a bot in 5 regions loads the login page and asserts it works — pages you at 3am even if no real user is online.
- **RUM:** JavaScript on the real site reports that users on a specific mobile carrier see 4s load times.

---

## Profiling in production

**Definition:** Measuring where a running program spends CPU time and allocates memory, often continuously, using low-overhead profilers.

**Simple explanation:** Metrics tell you a service is slow; a profiler tells you *which function* is slow. Continuous profilers (like Go's `pprof`, or continuous-profiling products) sample the running process cheaply so you can find hot code paths without a lab reproduction. Flame graphs visualize the call stacks eating the most time.

**Example:** A service's CPU is pinned. A flame graph from `pprof` shows 70% of time in a JSON-serialization function called in a loop — you cache the result and CPU drops by half.

---

## Anomaly detection

**Definition:** Automatically flagging metric behavior that deviates from a learned normal baseline, instead of using fixed thresholds.

**Simple explanation:** Static thresholds ("alert if > 1000 req/s") break when normal traffic varies by time of day. Anomaly detection learns the expected pattern (including daily/weekly seasonality) and alerts when reality diverges — catching both spikes *and* unexpected drops.

**Example:** Traffic normally dips at night. A fixed "too low" threshold would false-alarm nightly. An anomaly detector learns the nightly dip and instead alerts when 2pm traffic suddenly falls to nighttime levels — a real signal something upstream broke.
