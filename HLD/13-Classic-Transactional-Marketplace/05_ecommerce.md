# Design an E-commerce Platform (Amazon) 🔴

> **Crux:** Split **read-heavy catalog** (scale with cache/replicas) from **inventory at checkout** (stronger consistency) — browse AP, buy CP.

## Clarify (say this first)

**Functional**
- Catalog browse/search, cart, checkout, pay, order tracking, returns
- Sellers / multi-warehouse inventory (mention)
- Recommendations optional

**Non-functional**
- Browse: ultra-high QPS, eventual consistency OK
- Checkout inventory: no massive oversell; small oversell may be business-tolerated with cancel
- Peak events (Prime Day) 10–50×
- Cart sticky per user; orders durable

## Back-of-envelope

- 100M DAU × 50 page views → millions RPM reads; writes tiny fraction
- Catalog: denormalized product docs in search + cache
- Inventory updates: warehouse receiving + checkout reservations
- Order placement: thousands TPS peak — shard by order_id / customer

## API + data model

```text
GET  /products/{id}
GET  /search?q=
POST /cart/items
POST /checkout/sessions      # reserve inventory + price snapshot
POST /orders                 # pay + confirm
GET  /orders/{id}
```

| Entity | Key fields |
|--------|------------|
| Product | id, title, attrs, price (display) |
| Offer / SKU | sku, seller, warehouse_qty, reserved |
| Cart | user_id, items[], version |
| Reservation | id, sku, qty, expires_at, checkout_id |
| Order | id, items[], payment, state, ship_to |

## High-level architecture

```text
Client ──► CDN / Edge
         │
         ▼
      API GW ──► Catalog Svc ──► Cache + Search + Product DB (replicas)
              │
              ├──► Cart Svc ──► Redis/DB
              │
              └──► Checkout ──► Inventory Svc (CP-ish) ──► Payment ──► Order Svc
                                      │
                                 Warehouse WMS / async restock
```

## Deep dive: the crux

**Read scaling (catalog)**
- Cache-aside product pages; search index via CDC; CDN for static assets.
- Price/promo may be slightly stale on PDP — revalidate at checkout.

**Inventory consistency**
1. Soft **reserve** qty on checkout start (TTL).
2. Payment success → reserve→commit (decrement on-hand).
3. Expiry / abandon → release reserve.
4. Multi-warehouse: allocate by ETA/cost; reservation records per warehouse.

| Alternative | When to pick |
|-------------|--------------|
| Optimistic oversell + cancel | Fashion / high SKU churn |
| Hard reserve at add-to-cart | Scarce drops (bad UX otherwise) |
| Reserve at checkout only | Default general retail |
| Per-SKU single-row atomic counter | Hot SKU flash sales |

**Hot SKU:** queue or partitioned counters; don't let one popular ASIN lock a giant transaction.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Eventual catalog | Scale & latency | Occasional stale price/stock badge |
| Checkout reservation | Fewer oversells | Abandoned carts lock stock |
| Allow mild oversell | Conversion | Refunds / trust hit |
| Denormalized product docs | Fast PDP | Invalidation complexity |

## Failure modes & scale

- Cache stampede on viral product → soft TTL + singleflight
- Reserve without pay → TTL worker; idempotent checkout session
- Payment OK / order write fail → outbox + reconcile
- Warehouse partition → degrade to other warehouses or read-only browse
- Scale: shard inventory by sku hash; cart by user_id; orders by id; CQRS for order history

## Interview trigger phrase

> “I'd scale **catalog reads** with cache and search under eventual consistency, and treat **inventory reservation at checkout** as the strongly consistent path — browse AP, buy CP.”

## Exercise

1. Flash sale of 100 units, 50k buyers — inventory data structure and fair-enough approach.
2. Where do you re-check price so a stale PDP promo can't check out wrong?
3. How does multi-warehouse allocation interact with reservation TTL?
