# Card / Casino Games

> Deck, players, dealing, scoring — **Factory** (deck/hand setup) + **Strategy** (game rules). 🟡

## Scope / requirements

**In:** shuffle/deal, turns, evaluate hands, declare winner for one game variant (e.g. Blackjack or simple Poker showdown). Multi-game support via rules strategy.

**Out:** RNG certification, multi-table casino platform, real-money compliance — keep domain pure.

## Entities

| Entity | Owns |
|--------|------|
| `Card`, `Rank`, `Suit` | immutable value |
| `Deck` | ordered cards, shuffle, draw |
| `Hand` / `Player` | held cards |
| `Game` / engine | turn loop |
| `GameRules` (Strategy) | deal count, scoring, win check |
| `DeckFactory` | standard 52, with jokers, etc. |

## Invariants

- Drawing from empty deck fails clearly (or triggers reshuffle — declare).
- Cards dealt leave the deck (no duplicates in play).
- Scoring only via `GameRules` — UI doesn’t hardcode Blackjack 21.
- Immutability of `Card` helps safe sharing / testing.

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Rule variant | **Strategy** | Blackjack vs Poker vs War |
| Deck creation | **Factory** | 52-card vs short deck |
| Turn flow | State (optional) | Betting → Deal → Play → Settle |

## End-to-end flow

1. Factory builds deck → shuffle → rules.deal(players).
2. Players act per rules until terminal.
3. `rules.score(hands)` → winner; optionally reshuffle for next round.

## Skeletons

### Python

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import random


class Suit(Enum):
    C = "C"; D = "D"; H = "H"; S = "S"


@dataclass(frozen=True)
class Card:
    rank: int  # 1..13
    suit: Suit


class Deck:
    def __init__(self, cards: list[Card]):
        self._cards = list(cards)

    def shuffle(self, rng: random.Random | None = None) -> None:
        (rng or random).shuffle(self._cards)

    def draw(self) -> Card:
        if not self._cards:
            raise RuntimeError("empty deck")
        return self._cards.pop()


def standard_52() -> Deck:
    return Deck([Card(r, s) for s in Suit for r in range(1, 14)])


class GameRules(ABC):
    @abstractmethod
    def deal(self, deck: Deck, players: list) -> None: ...
    @abstractmethod
    def winner(self, players: list) -> object: ...


class HighCardWar(GameRules):
    def deal(self, deck: Deck, players: list) -> None:
        for p in players:
            p.hand = [deck.draw()]

    def winner(self, players: list):
        return max(players, key=lambda p: p.hand[0].rank)


class Game:
    def __init__(self, rules: GameRules, deck_factory=standard_52):
        self.rules = rules
        self.deck_factory = deck_factory

    def play_round(self, players: list):
        deck = self.deck_factory()
        deck.shuffle()
        self.rules.deal(deck, players)
        return self.rules.winner(players)
```

### Go

```go
type Card struct{ Rank int; Suit string }

type Deck struct{ cards []Card }

func Standard52() *Deck {
    suits := []string{"C", "D", "H", "S"}
    d := &Deck{}
    for _, s := range suits {
        for r := 1; r <= 13; r++ {
            d.cards = append(d.cards, Card{r, s})
        }
    }
    return d
}

func (d *Deck) Draw() (Card, error) {
    if len(d.cards) == 0 {
        return Card{}, fmt.Errorf("empty")
    }
    c := d.cards[len(d.cards)-1]
    d.cards = d.cards[:len(d.cards)-1]
    return c, nil
}

type GameRules interface {
    Deal(deck *Deck, players []*Player)
    Winner(players []*Player) *Player
}

type Game struct {
    Rules       GameRules
    DeckFactory func() *Deck
}
```

## Concurrency / consistency

- Usually single-threaded table actor — one game loop owns the deck.
- For multiplayer servers: serialize actions per table id; don’t share mutable `Deck` across tables.
- Seedable RNG for tests / replays.

## Tradeoffs / pitfalls

- Inheritance tree `BlackjackPlayer extends PokerPlayer` — prefer composition + rules Strategy.
- Mutable global deck singleton — nightmare for tests.
- Encoding Ace as both 1 and 11 only inside Blackjack strategy, not on `Card`.

## Interview prompts

- How do you add Blackjack without editing War?
- Where does Factory beat `new Deck()` everywhere?
- How would you support undo of a misdeal? (Memento / Command)

## Exercise / follow-ups

1. Implement Blackjack rules: hit/stand, Ace soft/hard, dealer stand on 17.
2. Add a `Shoe` (multiple decks) Factory.
3. Inject `rng` for deterministic tests.
