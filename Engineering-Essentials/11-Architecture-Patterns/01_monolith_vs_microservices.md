# Monolith vs Microservices

> One deployable vs many independently deployable services. The hard part isn't drawing boxes — it's **distributed complexity** (networks, data, ops).

## Plain English

A **monolith** is one codebase/process (or a modular monolith with clear modules, still one deploy). Simple transactions, one DB, one pipeline.

**Microservices** split by business capability into separately deployable services with their own data. You buy independent scale and team autonomy; you pay with network calls, eventual consistency, and more ops surface.

```text
  Monolith:     UI → App → DB          (one deploy, ACID easy)
  Microservices: UI → Gateway → Cart / Orders / Payments / Inventory
                              (many deploys, consistency is hard)
```

Default senior take: **start modular monolith**; split when a clear boundary + team/scale pain justifies the tax. Don't split because it's fashionable.

## Essentials (must-know for this topic)

### Comparison

| | **Monolith** | **Microservices** |
|---|--------------|-------------------|
| Deploy | One unit | Many independent deploys |
| Data | Usually one DB / easy ACID | Per-service data; eventual consistency |
| Consistency | Local transactions | Sagas, outbox, compensations |
| Scale | Scale the whole app | Scale hot services independently |
| Team | One codebase coordination | Team autonomy per service |
| Ops | Simpler | More pipelines, mesh, on-call surface |
| Failure | Process crash = big blast | Failure isolation *if* boundaries are real |

### Modular monolith (middle path)

| Idea | Meaning |
|------|---------|
| **Modular monolith** | Clear modules/boundaries, **one** deployable |
| Why seniors like it | Structure without distributed tax |
| Extract later | When a module has clear ownership + scale/release pain |

### When to choose what

| Prefer **monolith** when… | Prefer **microservices** when… |
|---------------------------|--------------------------------|
| Small team, unclear domain | Clear bounded contexts + multiple teams |
| Strong consistency needed often | Independent scale/release per domain |
| Ops maturity is low | Platform/SRE can run many services |
| Speed of iteration | Isolation of failure / blast radius |

## Simple example

Early startup: one Rails/Django/Spring app with modules `orders`, `billing`, `catalog` — fine.

Later: payments team needs weekly releases and PCI isolation; checkout traffic spikes independently → extract **payments** service with its own DB; keep catalog in the monolith until it hurts.

## Trade-offs

| Prefer **monolith** when… | Prefer **microservices** when… |
|---------------------------|--------------------------------|
| Small team, unclear domain | Clear bounded contexts + multiple teams |
| Strong consistency needed often | Independent scale/release per domain |
| Ops maturity is low | Platform/SRE can run many services |
| You need speed of iteration | You need isolation of failure/blast radius |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Microservices | Scale/team autonomy | Distributed transactions, debugging cost |
| Modular monolith | Clear structure, easy ACID | Single deploy blast radius / scale unit |
| Premature split | “Looks modern” | Latency, dual writes, on-call chaos |

## Pitfalls

- **Distributed monolith** — many services still coupled by shared DB or lockstep releases.
- **Splitting by technical layer** (all “controllers” vs “DB”) instead of by business capability.
- **Ignoring data ownership** — every service poking one shared database.
- **Assuming microservices = scalability** — a well-designed monolith scales far.

## Interview trigger phrase

> “I'd keep a **modular monolith** until a bounded context has clear ownership and scale/release pain — then extract that service with its **own data**, accepting eventual consistency across the rest.”

## Exercise

Marketplace with Catalog, Checkout, Payments, Reviews. Which one do you extract first and why? What do you leave in the monolith for another year?
