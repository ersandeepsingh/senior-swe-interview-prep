# Elevator System

> Multi-elevator scheduling & request dispatch → **State + Strategy (scheduling)**. 🔴

## Scope / Requirements

**In scope**
- N elevators, M floors; hall calls (up/down) and cabin floor requests.
- Each elevator has direction/state: idle, moving up/down, door open (simplified).
- Dispatcher assigns hall calls to an elevator via a scheduling strategy.
- Serve stops; don’t reverse until the current direction’s pending stops are done (SCAN-like).

**Out of scope**
- Real-time hardware, weight sensors, fire mode UI, persistence, fancy animations.

**Domain invariants**
- An elevator has one floor and one direction (or idle) at a time.
- Cabin requests are only valid floors in range.
- A hall call is completed when an elevator stops at that floor going the requested direction (or you simplify to “stop at floor”).
- Doors open only when stopped; movement only when doors closed.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Elevator` | Floor, direction, pending stops, door state; step simulation. |
| `ElevatorState` | Behavior for idle / moving / door open (optional full State). |
| `Request` / `HallCall` | Floor + direction (or cabin target). |
| `Dispatcher` / `ElevatorController` | Assign hall calls using strategy; tick all elevators. |
| `SchedulingStrategy` | Choose which elevator handles a hall call. |

## Key Interfaces / Patterns

- **State:** movement rules differ by Idle vs MovingUp/Down vs DoorOpen — prevents illegal transitions.
- **Strategy — `SchedulingStrategy`:** nearest-car, load-balanced, zone — interviewer probe for senior signal.
- **Command (optional):** enqueue floor requests as commands for testing/replay.

## End-to-End Flow

1. User presses hall button floor 5 UP → `Dispatcher.requestHall(5, UP)`.
2. Strategy scores elevators → assign to elevator E2 → E2 adds stop 5.
3. Simulation tick: E2 moves toward 5, opens door, completes call, then continues with cabin/hall stops in SCAN order.

## Python Skeleton

```python
from abc import ABC, abstractmethod
from enum import Enum, auto


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    IDLE = auto()


class Elevator:
    def __init__(self, eid: str, floors: int):
        self.id = eid
        self.floors = floors
        self.floor = 0
        self.direction = Direction.IDLE
        self.stops: set[int] = set()

    def add_stop(self, floor: int) -> None:
        if 0 <= floor < self.floors:
            self.stops.add(floor)
            if self.direction == Direction.IDLE and floor != self.floor:
                self.direction = Direction.UP if floor > self.floor else Direction.DOWN

    def step(self) -> None:
        if not self.stops:
            self.direction = Direction.IDLE
            return
        if self.floor in self.stops:
            self.stops.remove(self.floor)
            # door open/close elided
            if not self.stops:
                self.direction = Direction.IDLE
            return
        if self.direction == Direction.UP:
            self.floor += 1
        elif self.direction == Direction.DOWN:
            self.floor -= 1
        # SCAN: reverse when no stops ahead
        if self.direction == Direction.UP and not any(f > self.floor for f in self.stops):
            self.direction = Direction.DOWN if any(f < self.floor for f in self.stops) else Direction.IDLE
        elif self.direction == Direction.DOWN and not any(f < self.floor for f in self.stops):
            self.direction = Direction.UP if any(f > self.floor for f in self.stops) else Direction.IDLE


class SchedulingStrategy(ABC):
    @abstractmethod
    def choose(self, elevators: list[Elevator], floor: int, direction: Direction) -> Elevator: ...


class NearestCarStrategy(SchedulingStrategy):
    def choose(self, elevators: list[Elevator], floor: int, direction: Direction) -> Elevator:
        def score(e: Elevator) -> tuple:
            # prefer same direction / idle, then distance
            dir_penalty = 0 if e.direction in (Direction.IDLE, direction) else 10
            return (dir_penalty, abs(e.floor - floor), len(e.stops))
        return min(elevators, key=score)


class ElevatorController:
    def __init__(self, elevators: list[Elevator], strategy: SchedulingStrategy):
        self.elevators = elevators
        self.strategy = strategy

    def hall_call(self, floor: int, direction: Direction) -> str:
        e = self.strategy.choose(self.elevators, floor, direction)
        e.add_stop(floor)
        return e.id

    def cabin_request(self, elevator_id: str, floor: int) -> None:
        for e in self.elevators:
            if e.id == elevator_id:
                e.add_stop(floor)
                return

    def tick(self) -> None:
        for e in self.elevators:
            e.step()
```

## Go Skeleton

```go
package elevator

type Direction int

const (
    Idle Direction = iota
    Up
    Down
)

type Elevator struct {
    ID        string
    Floors    int
    Floor     int
    Direction Direction
    Stops     map[int]struct{}
}

func (e *Elevator) AddStop(floor int) {
    if floor < 0 || floor >= e.Floors {
        return
    }
    e.Stops[floor] = struct{}{}
    if e.Direction == Idle && floor != e.Floor {
        if floor > e.Floor {
            e.Direction = Up
        } else {
            e.Direction = Down
        }
    }
}

func (e *Elevator) Step() {
    if len(e.Stops) == 0 {
        e.Direction = Idle
        return
    }
    if _, ok := e.Stops[e.Floor]; ok {
        delete(e.Stops, e.Floor)
        return
    }
    if e.Direction == Up {
        e.Floor++
    } else if e.Direction == Down {
        e.Floor--
    }
}

type SchedulingStrategy interface {
    Choose(elevators []*Elevator, floor int, dir Direction) *Elevator
}

type NearestCar struct{}

func (NearestCar) Choose(elevators []*Elevator, floor int, dir Direction) *Elevator {
    best := elevators[0]
    bestDist := abs(best.Floor - floor)
    for _, e := range elevators[1:] {
        d := abs(e.Floor - floor)
        if d < bestDist {
            best, bestDist = e, d
        }
    }
    return best
}

type Controller struct {
    Elevators []*Elevator
    Strategy  SchedulingStrategy
}

func (c *Controller) HallCall(floor int, dir Direction) string {
    e := c.Strategy.Choose(c.Elevators, floor, dir)
    e.AddStop(floor)
    return e.ID
}

func (c *Controller) Tick() {
    for _, e := range c.Elevators {
        e.Step()
    }
}

func abs(x int) int {
    if x < 0 {
        return -x
    }
    return x
}
```

## Concurrency / Consistency

- Hall calls and ticks: single controller goroutine/thread is simplest (actor-style).
- If parallel, lock per elevator; dispatcher assignment must be atomic with stop insertion.
- Don’t let two strategies assign the same call twice — mark call pending/assigned.

## Extensions / Trade-offs / Pitfalls

- Zone strategy (elevator owns floors) vs nearest — throughput vs fairness.
- Full State objects vs direction enum — use State when door timing / maintenance modes matter.
- Pitfall: reversing direction mid-trip and stranding cabin requests.
- Simulation `tick()` vs event-driven time — pick one and stick to it in the interview.

## Interview Discussion Points

- SCAN vs LOOK vs shortest-seek — what are you optimizing (wait time vs fairness)?
- How do you model “elevator already going up past floor 5 shouldn’t take a down call at 5 yet”?
- Single dispatcher bottleneck — when would you shard by bank/zone?

## Exercise

Implement **2 elevators, 10 floors**: hall call + cabin request + `tick` until idle.

**Follow-ups**
1. Swap in a “least busy” strategy (min pending stops) without changing `HallCall` callers.
2. Add door-open dwell time as a state; list illegal transitions you prevent.
3. Explain how you’d unit-test scheduling without sleeping real time.
