# Prototype

> Create new objects by **cloning** an existing instance (the prototype) instead of constructing from scratch.

## Plain English

When setup is expensive or fiddly — a fully configured enemy, a document with styles, a connection template — copy a known-good instance and tweak the differences.

## Why seniors get asked this

Game entities, document templates, “duplicate this configured object” flows. Interviewers check if you know **shallow vs deep copy** and when cloning is safer than re-running a long setup.

## Real-world analogy

A **photocopy of a filled form**: you don’t retype every field; you copy and change the name.

## Example

### Python

```python
import copy
from dataclasses import dataclass, field


@dataclass
class Enemy:
    kind: str
    hp: int
    skills: list[str] = field(default_factory=list)

    def clone(self) -> "Enemy":
        return copy.deepcopy(self)


proto = Enemy("orc", 100, ["slash", "roar"])
a = proto.clone()
b = proto.clone()
a.hp = 80
a.skills.append("berserk")

assert b.hp == 100
assert b.skills == ["slash", "roar"]  # deep copy — independent
```

### Go

```go
type Enemy struct {
    Kind   string
    HP     int
    Skills []string
}

func (e Enemy) Clone() Enemy {
    skills := make([]string, len(e.Skills))
    copy(skills, e.Skills)
    return Enemy{Kind: e.Kind, HP: e.HP, Skills: skills}
}

proto := Enemy{Kind: "orc", HP: 100, Skills: []string{"slash", "roar"}}
a := proto.Clone()
b := proto.Clone()
a.HP = 80
a.Skills = append(a.Skills, "berserk")
// b unchanged
```

In Go, values already copy on assignment for structs; still deep-copy slices/maps yourself.

## When to use

- Constructing from scratch is costly or needs many steps; a seeded prototype is cheaper.
- You need many similar instances with small variations (spawn waves, document templates).
- Runtime registration of prototypes (registry of named templates to clone).

## When not to use / pitfalls

- Simple value objects → just construct; cloning adds confusion.
- **Shallow copy** sharing mutable nested state → bugs that look like “spooky action.”
- Circular references / resources (file handles, sockets) — clone carefully or don’t.
- Prefer a factory that builds from a config struct if that’s clearer than clone semantics.

## Interview trigger phrase

> “I’d keep a prototype of the configured enemy and deep-clone it per spawn so setup isn’t repeated — watching shared mutable state.”

## Exercise

A **document template** has title style, margins, and a list of default sections.

1. Implement `clone()` that doesn’t share the sections list between copies.
2. What breaks if you only shallow-copy?
3. When is a factory from JSON config better than Prototype?
