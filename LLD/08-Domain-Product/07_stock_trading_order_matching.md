# Stock Trading / Order Matching Engine

> Order book, match buy/sell — **priority queues** + **Strategy** (order types). 🔴

## Scope / requirements

**In:** place limit orders, maintain bids/asks, match when bid ≥ ask, produce trades, cancel resting orders. Optional: market orders that take liquidity.

**Out:** full exchange (clearing, margins, market data multicast) — keep to single-instrument book.

## Entities

| Entity | Owns |
|--------|------|
| `Order` | side, price, qty, remaining, type, timestamp |
| `OrderBook` | bids (max-heap), asks (min-heap) |
| `Trade` | price, qty, buy_id, sell_id |
| `MatchingEngine` | match loop |
| `OrderTypeStrategy` | limit vs market behavior |

## Invariants

- Bids sorted price **desc**, time **asc** for equal price; asks price **asc**, time **asc**.
- Trade price follows exchange rule (e.g. resting order price) — declare.
- `remaining >= 0`; filled orders leave the book.
- Never match same side; self-trade prevention optional (mention).

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Book structure | Two heaps / sorted maps | O(log n) insert, best price O(1)/O(log n) |
| Order type | **Strategy** | Limit / market / IOC |
| Trade listeners | **Observer** | Market data feed |

## End-to-end flow

1. Incoming buy limit → try match against best asks while price crosses → residual rests on bids.
2. Each match emits `Trade` and reduces remaining qty both sides.
3. Cancel removes from book if still resting.

## Skeletons

### Python

```python
import heapq
import itertools
from dataclasses import dataclass, field


@dataclass(order=True)
class Bid:
    neg_price: int
    seq: int
    order_id: str = field(compare=False)
    price: int = field(compare=False)
    qty: int = field(compare=False)


@dataclass(order=True)
class Ask:
    price: int
    seq: int
    order_id: str = field(compare=False)
    qty: int = field(compare=False)


class OrderBook:
    def __init__(self):
        self.bids: list[Bid] = []
        self.asks: list[Ask] = []
        self._seq = itertools.count()
        self.trades: list[tuple] = []

    def add_limit_buy(self, order_id: str, price: int, qty: int) -> None:
        while qty > 0 and self.asks and self.asks[0].price <= price:
            best = self.asks[0]
            traded = min(qty, best.qty)
            self.trades.append((order_id, best.order_id, best.price, traded))
            qty -= traded
            best.qty -= traded
            if best.qty == 0:
                heapq.heappop(self.asks)
        if qty > 0:
            heapq.heappush(self.bids, Bid(-price, next(self._seq), order_id, price, qty))

    def add_limit_sell(self, order_id: str, price: int, qty: int) -> None:
        while qty > 0 and self.bids and self.bids[0].price >= price:
            best = self.bids[0]
            traded = min(qty, best.qty)
            self.trades.append((best.order_id, order_id, best.price, traded))
            qty -= traded
            best.qty -= traded
            if best.qty == 0:
                heapq.heappop(self.bids)
        if qty > 0:
            heapq.heappush(self.asks, Ask(price, next(self._seq), order_id, qty))
```

### Go

```go
// Use container/heap for bids (max) and asks (min).
type MatchingEngine struct {
    Book *OrderBook
}

func (e *MatchingEngine) PlaceLimitBuy(id string, price, qty int) []Trade {
    var trades []Trade
    for qty > 0 {
        best, ok := e.Book.BestAsk()
        if !ok || best.Price > price {
            break
        }
        traded := min(qty, best.Qty)
        trades = append(trades, Trade{BuyID: id, SellID: best.ID, Price: best.Price, Qty: traded})
        qty -= traded
        e.Book.ReduceAsk(traded)
    }
    if qty > 0 {
        e.Book.RestBid(Order{ID: id, Price: price, Qty: qty})
    }
    return trades
}
```

## Concurrency / consistency

- Matching engine is usually **single-threaded per symbol** (actor / shard) — simplest correctness story.
- If multi-threaded, one mutex per book; never match across unlocked books.
- Incoming gateway may be concurrent; serialize onto the symbol’s queue.

## Tradeoffs / pitfalls

- Using unsorted lists — too slow and wrong for interviews unless N is tiny and you say so.
- Forgetting time priority at same price.
- Mutating heap entries incorrectly (need stale-skip or indexable heap for cancel).

## Interview prompts

- Why shard by symbol?
- Market order that walks the book — how?
- How do you cancel efficiently in a heap?

## Exercise / follow-ups

1. Implement market buy that consumes asks until qty filled or book empty.
2. Add trade Observer for a ticker tape.
3. Explain IOC (immediate-or-cancel) as a Strategy on place.
