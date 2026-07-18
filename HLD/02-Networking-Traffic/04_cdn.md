# CDN (Content Delivery Network)

> A **CDN** caches static (and sometimes dynamic) content at **edge PoPs** close to users — cutting latency and origin load for media, JS/CSS, thumbnails, and downloadable assets.

## Plain English

| Term | Meaning |
|------|---------|
| **Origin** | Your source of truth (S3, object store, app) |
| **Edge / PoP** | CDN node near the user |
| **Cache hit** | Served from edge — fast, cheap |
| **Cache miss / revalidate** | Fetch (or check) origin, then store at edge |
| **TTL / Cache-Control** | How long edge may keep a copy |
| **Purge / invalidate** | Force edges to drop stale objects after publish |

Best fit: **read-heavy, same bytes for many users**. Weak fit: per-user private HTML with no shared cache key.

```text
  User ──► nearest PoP ──► hit? ──yes──► response
                 │
                miss
                 │
                 ▼
              Origin (S3 / app)
                 │
                 └── populate edge ──► response
```

## Simple example

**News site + video thumbnails:**

```text
  www.news.com/app.js          → CDN, TTL 1y + content-hashed filename
  /images/hero-123.jpg         → CDN, TTL 1d, purge on editor replace
  /api/personalized-feed       → usually bypass CDN (or cache at gateway carefully)
  live-stream segments *.ts    → CDN with short TTL / packed playlists
```

Ship `app.<hash>.js` so you can use long TTL without “users stuck on old bundle.” Editors hit **purge** when replacing `hero-123.jpg` under the same URL.

## Why prefer one over the other

| Prefer **CDN** when… | Hit **origin / regional cache** when… |
|----------------------|----------------------------------------|
| Global static/media fan-out | Highly personalized or strongly consistent HTML |
| Origin bandwidth is expensive | Objects rarely reused across users |
| You need DDoS/TLS offload at edge | Compliance forces data to stay in-region only |

| Long TTL + hashed names | Short TTL / purge-heavy |
|-------------------------|-------------------------|
| Near-perfect hit rate | Fresher content, more origin traffic |
| Deploy = new URL | Operational purge complexity |

**Not “CDN replaces app cache.”** CDN is for *shared HTTP objects*. Redis is for *application data* and sessions.

### Interview checklist

- Cache-Control / ETag / immutable hashed filenames  
- Origin shield for viral misses  
- Separate behaviors for public vs private content (signed URLs)

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Edge caching | Lower TTFB; shield origin | Stale risk; purge races across PoPs |
| Origin shield (mid-tier) | Collapses thundering herd to origin | Extra hop on miss |
| Signed URLs / cookies | Protect paid media | More auth design at edge |
| Dynamic acceleration (proxy only) | Better routing/TLS | No cache benefit if uncacheable |

## Interview trigger phrase

> “I’d put **images, videos, and hashed static assets on a CDN** with long TTLs, purge on same-URL updates, and keep personalized API responses off the CDN unless we have an explicit cache key and TTL.”

## Exercise

**Design CDN for a photo-sharing app.**

1. Public thumbnails vs private original downloads — how do cache keys and signed URLs differ?  
2. A celebrity posts a photo that goes viral in one city — what protects the origin on the first wave of misses?  
3. You change CSS under `/static/app.css` (same URL) — what goes wrong with a 7-day TTL, and what’s the better naming strategy?
