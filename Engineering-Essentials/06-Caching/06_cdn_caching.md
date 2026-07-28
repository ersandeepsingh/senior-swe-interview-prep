# CDN Caching

> A **CDN** caches responses at **edge** locations close to users. Best for static assets and cacheable HTTP responses — offloads origin and cuts latency worldwide.

## Plain English

CDN = geographically distributed reverse proxies. User hits a nearby PoP; on miss, PoP fetches from origin (S3, app, API), stores, and serves the next users from the edge.

Controlled mainly by **HTTP cache headers**:

| Header | Role |
|--------|------|
| `Cache-Control: max-age=…, public/private` | Who may cache, for how long |
| `ETag` / `Last-Modified` | Conditional revalidation (`304`) |
| `Vary` | Separate variants (e.g. `Accept-Encoding`, `Authorization` — careful) |
| Surrogate / CDN-specific keys | Purge APIs, soft purge |

```text
  User → Edge PoP → (miss) → Origin
              │
           (hit) serve from edge
```

## Essentials (must-know for this topic)

### CDN vs app cache vs browser — three layers

| Layer | What it caches | Invalidation |
|-------|----------------|--------------|
| **Browser** | Per-user private/public responses | `Cache-Control`, hard refresh |
| **CDN edge** | Shared geographic copies | TTL, purge API, soft purge |
| **App Redis** | Personalized / computed objects | App delete / TTL |

### Headers & ideas you must name

| Header / idea | Role |
|---------------|------|
| `Cache-Control: max-age, public/private, no-store` | Who may cache, how long |
| `ETag` / `Last-Modified` | Conditional revalidation → `304` |
| `Vary` | Separate cache entries by header (abuse → fragmentation) |
| **Fingerprinted assets** | `app.abc123.js` → long TTL + `immutable` |
| **Purge / invalidate** | Force edge drop after publish/deploy |
| **Cache key** | URL + selected headers/query — wrong key = leaks or misses |

**Never** `public`-cache authenticated/personalized responses. HTML often short TTL + purge; hashed static assets long TTL.

## Simple example

**Media site:**

```text
  /static/app.js     Cache-Control: public, max-age=31536000, immutable  (fingered)
  /images/hero.jpg   public, max-age=86400
  /api/home          private or short max-age + purge on publish
  /api/me            Cache-Control: private, no-store
```

**HTML with fingerprinted assets:** HTML can be short TTL or purged on deploy; JS/CSS get long TTL because the filename changes when content changes.

## When to use / trade-offs

| Prefer **CDN** when… | Prefer **origin-only** when… |
|----------------------|------------------------------|
| Static/media, global users | Highly personalized, uncacheable responses |
| You can set clear TTLs / purge | Every byte is user-specific secrets |
| Origin bandwidth/cost hurts | Tiny regional audience, simple stack |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Long edge TTL | Hit rate, cheap | Stale until purge/expiry |
| Short TTL / revalidate | Fresher | More origin hits |
| Aggressive `Vary` | Correct variants | Cache fragmentation |
| Purge on publish | Fast freshness | Purge race, API limits |

## Pitfalls

- Caching **authenticated** responses as `public` → data leak across users.  
- `Vary: Cookie` or `Vary: *` → useless cache.  
- Forgetting purge after deploy → users stuck on old JS.  
- Putting CDN in front of APIs without thinking about **cache keys** (query strings, headers).  
- Confusing browser cache vs CDN vs app Redis — three layers, three invalidation stories.

## Interview trigger phrase

> “I’d put a **CDN** in front of static and cacheable GETs with **fingerprinted assets + long TTL**, short TTL or purge for HTML/API, and **never** cache personalized responses as public.”

## Exercise

**Design caching for a news homepage.**

1. Which layers: browser, CDN, Redis — what lives where?  
2. Breaking news update — how does the new headline reach users in &lt;30s?  
3. One mistaken `Cache-Control: public` on `/api/me` — what goes wrong?
