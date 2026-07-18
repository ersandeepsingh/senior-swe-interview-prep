# Design a Stock Exchange / Order Matching Engine 🔴

> **Crux:** **Ultra-low latency matching** with strict **ordering and consistency** per instrument — fairness and correctness beat generic web architecture.

## Clarify (say this first)

**Functional**
- Place/cancel limit & market orders; match trades; publish market data
- Order types: limit, market, IOC/FOK (scope which)
- Clearing/settlement out of scope or async downstream

**Non-functional**
- Latency: microseconds–low ms per match (state your tier: retail vs exchange-grade)
- **Total order** of events per symbol; deterministic matching
- Durability of accepted orders & trades; no lost fills
- Fairness: FIFO or pro-rata rules — name the rule
- Throughput: millions of orders/day concentrated on hot symbols

## Back-of-envelope

- Hot symbol: tens of thousands of orders/s bursts
- Market data fan-out >> matching input
- Persistence: sequential write log; replay for recovery
- Cannot naively shard one symbol across matchers (breaks price-time priority)

## API + data model

```text
POST /orders                  # side, type, price, qty, symbol, client_order_id
DELETE /orders/{id}           # cancel
GET  /orders/{id}
WS   /md/{symbol}             # L2 book / trades
```

| Entity | Key fields |
|--------|------------|
| Order | id, symbol, side, price, qty, remaining, status, ts_seq |
| OrderBook | symbol → bids (desc) + asks (asc) priority queues |
| Trade | id, buy_order, sell_order, price, qty, seq |
| Seq / Gate | symbol, last_seq |

## High-level architecture

```text
Clients ──► Gateway (auth, risk checks) ──► Sequencer / Input Q (per symbol)
                                                │
                                                ▼
                                         Matching Engine
                                         (single writer / symbol)
                                           │         │
                                           ▼         ▼
                                      Trade Log    Market Data Bus
                                           │
                                           ▼
                                      Drop-copy / Clearing
```

## Deep dive: the crux

**Ordering + consistency**
- **Single-threaded matcher per symbol** (or lock-free single writer): assign monotonic seq; process order/cancel/trade deterministically.
- Persist **WAL / event log** before ACK (or ACK with careful replication protocol).
- Replication: primary-backup with sync or Raft for exchange-grade durability.

**Matching**
- Price-time priority: best price first; same price → earlier seq wins.
- Market order walks book until filled or reject per rules.

| Alternative | When to pick |
|-------------|--------------|
| DB row locks as “book” | Never for real exchange |
| In-memory book + WAL + single writer | Default serious design |
| Sharded by symbol | Horizontal scale across tickers |
| FPGA / kernel bypass | Exchange-grade latency arms race |

**Idempotency:** `client_order_id` unique per session to dedupe retries.

## Trade-offs

| Decision | Gain | Give up |
|----------|------|---------|
| Single writer / symbol | Correct priority & simplicity | Ceiling on one hot ticker's core |
| Sync disk before ACK | Durability | Latency |
| Async market data | Matcher isolation | MD lag vs trade truth |
| In-process risk checks | Fast reject | Coupled blast radius |

## Failure modes & scale

- Primary crash → promote replica from log; replay to rebuild book
- Slow consumer of MD → drop or conflate snapshots; never block matcher
- Poison order → risk limits at gateway; isolate symbol if needed
- Hot symbol CPU bound → vertical scale; careful NUMA; not horizontal split of one book
- Scale elsewhere: many symbols × many engines; separate MD cluster; gateway horizontally

## Interview trigger phrase

> “I'd run a **single-writer matching engine per symbol** over a sequenced log — in-memory order book for latency, **WAL for durability**, and market data as a downstream projection.”

## Exercise

1. Why sharding one symbol's book across two matchers breaks price-time priority.
2. Crash after match in memory but before WAL — what must the protocol guarantee?
3. How do cancel and incoming aggressive order interleave safely under one seq?
