# Composition over Inheritance

> Prefer **has-a** (compose behaviors) over deep **is-a** trees.

## Plain English

Inheritance couples you to a parent forever. Composition lets you plug in abilities: a character *has* a weapon and *has* a movement style — instead of `FlyingFireBreathingBossEnemy extends …`.

In Go this is the default (embedding + interfaces). In Python/Java, people overuse `extends`.

## Why seniors get asked this

Game characters, notification channels, pricing rules — interviewers watch whether you build a brittle hierarchy or flexible parts.

## Bad: deep inheritance for behavior combos

### Python

```python
class Character:
    def attack(self) -> str:
        return "punch"


class Flyer(Character):
    def move(self) -> str:
        return "fly"


class Swimmer(Character):
    def move(self) -> str:
        return "swim"


# Need a flying swimmer? Or flyer with sword?
# Explosion of subclasses: FlyingSwordGuy, SwimmingAxeGuy, ...
class FlyingSwordCharacter(Flyer):
    def attack(self) -> str:
        return "sword slash"
```

Combinations explode. Changing `Flyer.move` risks everything that inherits it.

### Go

Inheritance isn’t the idiomatic path; the bad smell is still **one mega-struct with every behavior** or fake hierarchies via embedding everything.

```go
type MegaCharacter struct {
    // everything dumped here — hard to reuse pieces
    CanFly, CanSwim bool
    Weapon          string
}
```

## Good: compose small behaviors

### Python

```python
from abc import ABC, abstractmethod


class Attack(ABC):
    @abstractmethod
    def hit(self) -> str: ...


class Movement(ABC):
    @abstractmethod
    def move(self) -> str: ...


class Punch(Attack):
    def hit(self) -> str:
        return "punch"


class Sword(Attack):
    def hit(self) -> str:
        return "sword slash"


class Walk(Movement):
    def move(self) -> str:
        return "walk"


class Fly(Movement):
    def move(self) -> str:
        return "fly"


class Character:
    def __init__(self, name: str, attack: Attack, movement: Movement):
        self.name = name
        self._attack = attack
        self._movement = movement

    def perform_attack(self) -> str:
        return f"{self.name}: {self._attack.hit()}"

    def travel(self) -> str:
        return f"{self.name}: {self._movement.move()}"


hero = Character("Asha", Sword(), Fly())
print(hero.perform_attack())  # Asha: sword slash
print(hero.travel())          # Asha: fly

# New combo = new wiring, not a new subclass tree
scout = Character("Dev", Punch(), Walk())
```

### Go

```go
type Attack interface{ Hit() string }
type Movement interface{ Move() string }

type Punch struct{}
func (Punch) Hit() string { return "punch" }

type Sword struct{}
func (Sword) Hit() string { return "sword slash" }

type Walk struct{}
func (Walk) Move() string { return "walk" }

type Fly struct{}
func (Fly) Move() string { return "fly" }

type Character struct {
    Name     string
    Attack   Attack
    Movement Movement
}

func (c Character) PerformAttack() string {
    return c.Name + ": " + c.Attack.Hit()
}

func (c Character) Travel() string {
    return c.Name + ": " + c.Movement.Move()
}

hero := Character{Name: "Asha", Attack: Sword{}, Movement: Fly{}}
```

## When inheritance is still OK

- True “is-a” with shared contract (LSP holds)
- Framework hooks (`Exception`, UI widgets) where the platform expects a subclass
- Very shallow trees (1 level), not behavior matrices

## Interview trigger phrase

> “I’d model variable behavior as composable strategies, not a deep inheritance tree.”

## Exercise

Design `Notification`: can be Email / SMS / Push, and can be Plain / HTML / Templated body.

1. Show why inheritance for every combo is a bad idea (count the classes).
2. Sketch composition: `Channel` + `Formatter` (Python or Go).
3. How would you add “Slack” without touching existing formatters?
