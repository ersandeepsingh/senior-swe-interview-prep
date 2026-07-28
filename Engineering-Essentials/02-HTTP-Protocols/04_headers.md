# Headers

> Metadata on requests/responses: **caching, content type, auth, CORS, compression** — the dials that make HTTP efficient and safe in browsers.

## Plain English

Headers are key/value pairs that steer caching, security, content negotiation, and auth — without changing the URL. Seniors tune `Cache-Control` and explain CORS preflight.

## Essentials (must-know for this topic)

### Header families

| Family | Key headers | Job |
|--------|-------------|-----|
| **Caching** | `Cache-Control`, `ETag`, `If-None-Match`, `Last-Modified`, `Vary` | Freshness + validation |
| **Content** | `Content-Type`, `Accept`, `Content-Encoding` | Negotiation + compression |
| **Auth** | `Authorization` | Bearer/JWT/Basic |
| **CORS** | `Origin`, `Access-Control-*` | Browser cross-origin rules |
| **Security** | `Strict-Transport-Security`, `Content-Security-Policy` | HTTPS / XSS posture |
| **Tracing** | `X-Request-Id`, `traceparent` | Correlate logs |

### Cache-Control quick map

| Directive | Meaning |
|-----------|---------|
| `public` | Shared caches (CDN) OK |
| `private` | Browser only — personalized |
| `no-store` | Don’t write to cache |
| `no-cache` | Must revalidate before use |
| `max-age=N` | Fresh for N seconds |
| `immutable` | Fingerprinted asset won’t change |

**Conditional GET:** client sends `If-None-Match: "etag"` → `304` saves bandwidth.

### CORS essentials

| Concept | Meaning |
|---------|---------|
| **Simple request** | Certain GET/POST — may skip preflight |
| **Preflight** | `OPTIONS` asks if `POST` + custom headers allowed |
| **Allow-Origin** | Exact origin or `*` — **never `*` with credentials** |

### Content negotiation

Client: `Accept: application/json` + `Accept-Encoding: gzip`. Server picks representation and may set `Vary: Accept-Encoding` (or `Origin`) when responses differ.

## Why seniors get asked

Caching and CORS bugs are everyday production issues. Seniors tune `Cache-Control` and explain preflight.

## Simple example

```http
GET /static/app.js HTTP/1.1
If-None-Match: "v42"

HTTP/1.1 304 Not Modified
ETag: "v42"
Cache-Control: public, max-age=31536000, immutable
```

```http
# CORS preflight
OPTIONS /api/orders HTTP/1.1
Origin: https://app.example.com
Access-Control-Request-Method: POST

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Authorization, Content-Type
```

```bash
curl -H "Accept-Encoding: gzip" -H "Accept: application/json" https://api.example.com/orders/42 -v
```

## When to use / when not / trade-offs

| Header strategy | When |
|-----------------|------|
| Long `max-age` + fingerprint filenames | Static assets |
| `private, no-store` | Personalized / sensitive responses |
| ETag validation | Content changes occasionally; save bandwidth |
| Compress (`gzip`/`br`) | Text JSON/HTML; skip already-compressed images |

**Trade-off:** aggressive caching = speed + risk of serving stale personalized data if mis-tagged `public`.

## Common pitfalls

- `Access-Control-Allow-Origin: *` with credentials
- Caching `Authorization` responses at a shared CDN
- Forgetting `Vary: Accept-Encoding` (or `Origin`) when responses differ
- Huge custom headers on every request (HPACK helps, still wasteful)

## Interview trigger phrase

> “I’d set Cache-Control and ETags for static/public data, and treat CORS as an allowlist — never * with cookies.”

## Exercise

A JSON API is personalized per user but a CDN caches it and users see each other’s data. Which headers were wrong, and what would you set instead?
