# 2. Networking & Traffic Management

How requests find healthy capacity, survive overload, and stay cheap at the edge. Interviewers expect you to **place LBs, gateways, CDN, and rate limits on the diagram** and say *why* each exists.

| # | Concept | One-line intent |
|---|---------|-----------------|
| 01 | [Load balancing](01_load_balancing.md) | L4 vs L7; RR / least-conn / consistent-hash |
| 02 | [Reverse proxy & API gateway](02_reverse_proxy_api_gateway.md) | Front door: routing, auth, throttling for microservices |
| 03 | [DNS & GeoDNS](03_dns_geodns.md) | Name resolution + geo-routing to nearest region |
| 04 | [CDN](04_cdn.md) | Edge cache for static assets and media |
| 05 | [Rate limiting](05_rate_limiting.md) | Token bucket / sliding window — protect yourself |
| 06 | [Backpressure & load shedding](06_backpressure_load_shedding.md) | Drop or delay under overload before meltdown |
| 07 | [Connection handling](07_connection_handling.md) | Keep-alive, pooling, WebSockets |

**How to use:** For each file — read Plain English → diagram → trade-offs → say the interview trigger phrase out loud → do the Exercise without peeking at notes.
