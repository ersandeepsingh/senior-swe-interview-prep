# `make` vs `new`

> `make` creates and initializes **slice, map, or channel** values (ready to use) and returns the value itself. `new(T)` allocates zeroed storage for any type and returns `*T`. For slices/maps/chans you almost always want `make`, not `new`.

## Plain English

`make([]int, 0, 8)` builds a slice header pointing at a zeroed backing array. `make(map[string]int)` builds an empty usable map. `make(chan int, 2)` builds a channel.

`new(int)` gives `*int` pointing at `0`. `new([]int)` gives a pointer to a **nil** slice header — still not a usable populated slice. `new(map[string]int)` points at a nil map — writes through it still panic.

Rule of thumb: `make` for the three built-in reference-ish types; `&T{}` or `new(T)` when you need a pointer to a zero struct/value.

## Interviewer Angle

- Why doesn’t `new` work well for maps?
- Return types of `make` vs `new`?
- Is `new` common in modern Go? (rare — prefer `&Type{}`)
- `make([]T, len, cap)` vs `make([]T, len)`?

## Go Examples

```go
s := make([]int, 5)       // len=5, cap=5, zeros
s2 := make([]int, 0, 5)   // len=0, cap=5
m := make(map[string]int) // ready for m["a"]=1
ch := make(chan int, 1)   // buffered channel

p := new(int)  // *int → 0
*p = 7

type User struct{ Name string }
u := new(User)   // *User with Name ""
u2 := &User{}    // idiomatic equivalent
```

```go
// Almost never what you want:
pm := new(map[string]int) // *map — map value is nil
// (*pm)["x"] = 1 // panic: assignment to entry in nil map
*pm = make(map[string]int)
(*pm)["x"] = 1 // works, but just use make to begin with
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| `new` for map/slice/chan | Extra indirection + still need `make` |
| `make([]T, N)` when you meant capacity only | Pre-fills len with zeros — appends after zeros |
| Confusing allocation with initialization | `new` only zeroes |

## Trigger Phrase

> “`make` initializes slices, maps, and channels and returns the value; `new` returns a pointer to zeroes. I use `make` for those three and `&T{}` for struct pointers.”

## Exercise

For each line, say what type you get and whether a write is safe:

```go
a := make([]int, 0)
b := new([]int)
c := make(map[int]int)
d := new(map[int]int)
e := make(chan int)
```
