# Tic-Tac-Toe / Chess

> Board, moves, rules, win-check → **Strategy (rules) + State**. 🟡🔴  
> Interview tip: nail **Tic-Tac-Toe** end-to-end; treat **Chess** as the same skeleton with a heavier `RulesEngine`.

## Scope / Requirements

**In scope (Tic-Tac-Toe)**
- 3×3 board; two players X/O; alternate turns; detect win/draw.
- Reject illegal moves (occupied / out of bounds / wrong turn).

**In scope (Chess — discuss / stub)**
- Piece types with move generation; check/checkmate; turn + castling/en passant as extensions.

**Out of scope**
- AI ratings, online matchmaking, full FIDE edge cases unless asked.

**Domain invariants (TTT)**
- Cell empty before place; marks only on current player’s turn.
- Game state: InProgress → Won(player) | Draw; no moves after terminal.
- Win = 3-in-row; draw = full board without win.

**Domain invariants (Chess, call out)**
- Own king must not be left in check after a move.
- Piece movement constrained by type + path clear (sliding pieces).
- Exactly one legal side to move.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Board` | Grid storage; place/get; copy for simulation. |
| `Player` / `Mark` | Identity. |
| `Move` | Coordinates (+ piece info for chess). |
| `Rules` / `GameRules` | Legal move? Winner? Draw? |
| `Game` | State + apply move + switch turn. |
| Chess: `Piece`, `MoveGenerator` | Per-piece strategy. |

## Key Interfaces / Patterns

- **Strategy — rules / piece moves:** TTT win strategy vs chess piece generators.
- **State:** InProgress / Finished — block moves.
- **Command + Memento (optional):** undo for editors/puzzles.
- Chess: **Factory** for pieces from FEN.

## End-to-End Flow (Tic-Tac-Toe)

1. Create game; current = X.
2. `play(0,0)` → rules validate → place → check win/draw → switch or finish.
3. Continue until terminal state.

## Python Skeleton (Tic-Tac-Toe + chess hook)

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto


class Mark(Enum):
    X = "X"
    O = "O"
    EMPTY = "."


class GameStatus(Enum):
    IN_PROGRESS = auto()
    WON = auto()
    DRAW = auto()


class Board:
    def __init__(self, n: int = 3):
        self.n = n
        self.cells = [[Mark.EMPTY] * n for _ in range(n)]

    def get(self, r: int, c: int) -> Mark:
        return self.cells[r][c]

    def place(self, r: int, c: int, m: Mark) -> None:
        self.cells[r][c] = m

    def full(self) -> bool:
        return all(self.cells[r][c] != Mark.EMPTY for r in range(self.n) for c in range(self.n))


class Rules(ABC):
    @abstractmethod
    def legal(self, board: Board, r: int, c: int, mark: Mark) -> bool: ...
    @abstractmethod
    def winner(self, board: Board) -> Mark | None: ...


class TicTacToeRules(Rules):
    def legal(self, board: Board, r: int, c: int, mark: Mark) -> bool:
        return 0 <= r < board.n and 0 <= c < board.n and board.get(r, c) == Mark.EMPTY

    def winner(self, board: Board) -> Mark | None:
        lines = []
        n = board.n
        lines.extend([[(i, j) for j in range(n)] for i in range(n)])
        lines.extend([[(i, j) for i in range(n)] for j in range(n)])
        lines.append([(i, i) for i in range(n)])
        lines.append([(i, n - 1 - i) for i in range(n)])
        for line in lines:
            marks = [board.get(r, c) for r, c in line]
            if marks[0] != Mark.EMPTY and all(m == marks[0] for m in marks):
                return marks[0]
        return None


class Game:
    def __init__(self, rules: Rules):
        self.board = Board()
        self.rules = rules
        self.current = Mark.X
        self.status = GameStatus.IN_PROGRESS
        self.winner: Mark | None = None

    def play(self, r: int, c: int) -> GameStatus:
        if self.status != GameStatus.IN_PROGRESS:
            raise RuntimeError("game over")
        if not self.rules.legal(self.board, r, c, self.current):
            raise RuntimeError("illegal")
        self.board.place(r, c, self.current)
        w = self.rules.winner(self.board)
        if w:
            self.status, self.winner = GameStatus.WON, w
            return self.status
        if self.board.full():
            self.status = GameStatus.DRAW
            return self.status
        self.current = Mark.O if self.current == Mark.X else Mark.X
        return self.status


# --- Chess seam (sketch) ---
class Piece(ABC):
    def __init__(self, color: str):
        self.color = color

    @abstractmethod
    def pseudo_legal(self, board, r: int, c: int) -> list[tuple[int, int]]: ...


class ChessRules(Rules):
    """Interview narrative: generate pseudo-legal → filter self-check → detect mate."""

    def legal(self, board: Board, r: int, c: int, mark: Mark) -> bool:
        raise NotImplementedError("use Move(from,to) API for chess")

    def winner(self, board: Board) -> Mark | None:
        return None
```

## Go Skeleton

```go
package tictactoe

import "errors"

type Mark byte

const (
    Empty Mark = '.'
    X     Mark = 'X'
    O     Mark = 'O'
)

type Status int

const (
    InProgress Status = iota
    Won
    Draw
)

type Board struct {
    N     int
    Cells [][]Mark
}

func NewBoard(n int) *Board {
    b := &Board{N: n, Cells: make([][]Mark, n)}
    for i := range b.Cells {
        b.Cells[i] = make([]Mark, n)
        for j := range b.Cells[i] {
            b.Cells[i][j] = Empty
        }
    }
    return b
}

type Rules interface {
    Legal(b *Board, r, c int) bool
    Winner(b *Board) (Mark, bool)
}

type TicTacToeRules struct{}

func (TicTacToeRules) Legal(b *Board, r, c int) bool {
    return r >= 0 && c >= 0 && r < b.N && c < b.N && b.Cells[r][c] == Empty
}

func (TicTacToeRules) Winner(b *Board) (Mark, bool) {
    lines := [][][2]int{}
    for i := 0; i < b.N; i++ {
        row, col := make([][2]int, b.N), make([][2]int, b.N)
        for j := 0; j < b.N; j++ {
            row[j] = [2]int{i, j}
            col[j] = [2]int{j, i}
        }
        lines = append(lines, row, col)
    }
    diag1, diag2 := make([][2]int, b.N), make([][2]int, b.N)
    for i := 0; i < b.N; i++ {
        diag1[i] = [2]int{i, i}
        diag2[i] = [2]int{i, b.N - 1 - i}
    }
    lines = append(lines, diag1, diag2)
    for _, line := range lines {
        m := b.Cells[line[0][0]][line[0][1]]
        if m == Empty {
            continue
        }
        ok := true
        for _, rc := range line[1:] {
            if b.Cells[rc[0]][rc[1]] != m {
                ok = false
                break
            }
        }
        if ok {
            return m, true
        }
    }
    return Empty, false
}

type Game struct {
    Board   *Board
    Rules   Rules
    Current Mark
    Status  Status
    Winner  Mark
}

func NewGame(r Rules) *Game {
    return &Game{Board: NewBoard(3), Rules: r, Current: X, Status: InProgress}
}

func (g *Game) Play(r, c int) error {
    if g.Status != InProgress {
        return errors.New("game over")
    }
    if !g.Rules.Legal(g.Board, r, c) {
        return errors.New("illegal")
    }
    g.Board.Cells[r][c] = g.Current
    if w, ok := g.Rules.Winner(g.Board); ok {
        g.Status, g.Winner = Won, w
        return nil
    }
    full := true
    for i := 0; i < g.Board.N; i++ {
        for j := 0; j < g.Board.N; j++ {
            if g.Board.Cells[i][j] == Empty {
                full = false
            }
        }
    }
    if full {
        g.Status = Draw
        return nil
    }
    if g.Current == X {
        g.Current = O
    } else {
        g.Current = X
    }
    return nil
}
```

## Concurrency / Consistency

- Authoritative game server serializes moves per game id.
- Chess clocks: separate timer concern; don’t mix into rules validation.

## Extensions / Trade-offs / Pitfalls

- N×N K-in-a-row: generalize win check.
- Chess: separate **pseudo-legal** from **legal** (filters check) — senior signal.
- Pitfall: mutating board before legality check without rollback.
- Undo: Command stack of moves.

## Interview Discussion Points

- Where does win detection live — `Board` or `Rules`? (prefer Rules)
- How would you plug chess pieces without a giant switch?
- TDD path: illegal move → win on row → draw.

## Exercise

Implement TTT with win/draw; write 3 unit-style scenarios mentally or in code.

**Follow-ups**
1. Generalize to N×N get-K-in-a-row.
2. Add undo via a move stack.
3. For chess, outline interfaces: `Piece.PseudoLegal`, `InCheck`, `ApplyMove` — no need for full implementation.
