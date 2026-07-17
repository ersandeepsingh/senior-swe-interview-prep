# Snake & Ladder / Board Games

> Turn engine, dice, entities → **composition + state**. 🟡

## Scope / Requirements

**In scope**
- N players, board 1..100 (configurable), snakes/ladders as teleports.
- Dice roll; move; apply snake/ladder; detect winner (exact land on end optional).
- Turn-based game loop until win.

**Out of scope**
- UI graphics, multiplayer networking, power-ups (unless asked).

**Domain invariants**
- One token position per player in `1..last` (or 0 start).
- Snakes map head → tail with head > tail; ladders start < end; no cycles preferred.
- Exactly one player’s turn at a time; turn advances after a completed move (or extra turn rule if stated).
- Win when position == last (or ≥ last if rule allows).

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Board` | Size + snake/ladder map. |
| `Dice` | Roll abstraction (testable). |
| `Player` | Id + position. |
| `Game` | Turn order, apply move, win check — state: Running/Finished. |
| `MoveRule` (optional) | Exact end, bounce-back, etc. Strategy. |

## Key Interfaces / Patterns

- **Composition:** `Game` has `Board`, `Dice`, `Players` — not inheritance of game types.
- **State:** Running vs Finished (ignore rolls after win).
- **Strategy:** win/move rules; dice (fair vs loaded for tests).
- Same skeleton extends to other board games with different move rules.

## End-to-End Flow

1. Init board with snakes/ladders; players at 0.
2. Player rolls dice → tentative position → if snake/ladder, teleport → if win, finish.
3. Next player until `Finished`.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import random


class Dice(ABC):
    @abstractmethod
    def roll(self) -> int: ...


class FairDice(Dice):
    def __init__(self, faces: int = 6):
        self.faces = faces

    def roll(self) -> int:
        return random.randint(1, self.faces)


@dataclass
class Board:
    size: int
    portals: dict[int, int] = field(default_factory=dict)  # from -> to

    def resolve(self, pos: int) -> int:
        return self.portals.get(pos, pos)


@dataclass
class Player:
    name: str
    position: int = 0


class MoveRule(ABC):
    @abstractmethod
    def next_position(self, current: int, roll: int, size: int) -> int: ...


class ExactEndRule(MoveRule):
    def next_position(self, current: int, roll: int, size: int) -> int:
        nxt = current + roll
        return current if nxt > size else nxt  # must land exact


class Game:
    def __init__(self, board: Board, players: list[Player], dice: Dice, rule: MoveRule):
        self.board = board
        self.players = players
        self.dice = dice
        self.rule = rule
        self.turn = 0
        self.winner: Player | None = None

    @property
    def finished(self) -> bool:
        return self.winner is not None

    def play_turn(self) -> dict:
        if self.finished:
            raise RuntimeError("game over")
        p = self.players[self.turn]
        roll = self.dice.roll()
        tentative = self.rule.next_position(p.position, roll, self.board.size)
        p.position = self.board.resolve(tentative)
        result = {"player": p.name, "roll": roll, "position": p.position}
        if p.position == self.board.size:
            self.winner = p
            result["won"] = True
        else:
            self.turn = (self.turn + 1) % len(self.players)
        return result

    def run(self) -> Player:
        while not self.finished:
            self.play_turn()
        return self.winner
```

## Go Skeleton

```go
package snakeladder

import "math/rand"

type Dice interface{ Roll() int }

type FairDice struct{ Faces int }

func (d FairDice) Roll() int { return rand.Intn(d.Faces) + 1 }

type Board struct {
    Size    int
    Portals map[int]int
}

func (b Board) Resolve(pos int) int {
    if to, ok := b.Portals[pos]; ok {
        return to
    }
    return pos
}

type Player struct {
    Name     string
    Position int
}

type MoveRule interface {
    Next(current, roll, size int) int
}

type ExactEnd struct{}

func (ExactEnd) Next(current, roll, size int) int {
    if current+roll > size {
        return current
    }
    return current + roll
}

type Game struct {
    Board   Board
    Players []*Player
    Dice    Dice
    Rule    MoveRule
    Turn    int
    Winner  *Player
}

func (g *Game) PlayTurn() (player string, roll, pos int, won bool) {
    if g.Winner != nil {
        return "", 0, 0, false
    }
    p := g.Players[g.Turn]
    roll = g.Dice.Roll()
    p.Position = g.Board.Resolve(g.Rule.Next(p.Position, roll, g.Board.Size))
    if p.Position == g.Board.Size {
        g.Winner = p
        return p.Name, roll, p.Position, true
    }
    g.Turn = (g.Turn + 1) % len(g.Players)
    return p.Name, roll, p.Position, false
}
```

## Concurrency / Consistency

- Single-threaded turn loop is correct; don’t parallelize turns.
- If networked, server is authority for dice + position (anti-cheat).

## Extensions / Trade-offs / Pitfalls

- Extra turn on 6; three 6s → cancel — Strategy/hooks on roll.
- Cycle detection when adding portals.
- Pitfall: applying snake after win check incorrectly; order is move → portal → win.
- Reuse for Ludo: multiple tokens + yard rules via different `MoveRule` / piece model.

## Interview Discussion Points

- Why inject `Dice` instead of `random` inside `Game`?
- Composition vs `class SnakeLadderGame extends BoardGame` hierarchy?
- How do you unit-test a full game deterministically?

## Exercise

Build a 1..100 board with 2 snakes, 2 ladders, 2 players; run until win with a seeded dice.

**Follow-ups**
1. Add “must roll exact to finish” as a swappable rule.
2. Detect and reject portal maps that contain cycles.
3. Sketch what you’d change for a generic “board game engine.”
