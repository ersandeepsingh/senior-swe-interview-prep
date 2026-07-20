# Zero Values & nil

> Every type has a **zero value**. For pointers, slices, maps, channels, functions, and interfaces, zero is **`nil`**. Nil and empty are not always the same: a nil slice and an empty slice both have `len == 0` but differ under `== nil` and JSON encoding.

## Plain English

| Type | Zero | Notes |
|------|------|-------|
| numbers | `0` | |
| bool | `false` | |
| string | `""` | |
| pointer | `nil` | deref panics |
| slice | `nil` | range OK; append OK; `== nil` |
| map | `nil` | read OK; **write panics** |
| channel | `nil` | send/receive **block forever** |
| func | `nil` | call panics |
| interface | `nil` | no type/value |

Empty slice: `[]int{}` or `make([]int, 0)` — not nil. Prefer nil slices until you need non-nil JSON `[]` or non-nil distinctions.

Nil channel in `select` is useful: disabled case. Nil channel outside select often deadlocks.

## Interviewer Angle

- Nil vs empty slice in JSON?
- Nil map write?
- Nil channel behavior?
- Zero value usefulness in API design?

## Go Examples

```go
var s []int
fmt.Println(s == nil, len(s)) // true, 0
s = append(s, 1)              // OK

var m map[string]int
fmt.Println(m["x"]) // 0
// m["x"] = 1      // panic

var ch chan int
// <-ch  // blocks forever
// ch <- 1 // blocks forever

select {
case <-ch: // never selected if ch nil
default:
}
```

```go
// JSON
var a []int          // null
b := []int{}         // []
data, _ := json.Marshal(a)
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Assuming nil slice needs `make` before append | Append handles nil |
| Assuming nil map accepts writes | Panic |
| Leaving nil channel in non-select code | Deadlock |
| Typed nil in interface | See interfaces section |

## Trigger Phrase

> “Zero values are usable defaults — nil slice is fine for append, nil map isn’t for write, nil chan blocks. I distinguish nil vs empty when APIs or JSON care.”

## Exercise

Fill a table for nil slice, empty slice, nil map, empty map, nil chan: what does `len`, range, read, write/send, and `json.Marshal` do for each?
