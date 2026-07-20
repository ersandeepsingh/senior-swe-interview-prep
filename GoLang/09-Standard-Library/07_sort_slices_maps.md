# `sort` / `slices` / `maps` — Ordering & Generic Helpers

> Sort with **`sort`** or generic **`slices`**; use **`maps`** for keys/values/clone/equal helpers (Go 1.21+).

## Plain English

Historically you implemented `sort.Interface` (`Len`/`Less`/`Swap`) or used `sort.Slice` with a less func. Go 1.21+ added `slices` and `maps` in the stdlib — prefer them for new code: clearer, generic, less boilerplate.

## Why interviewers ask

Custom ordering shows up in coding rounds. Knowing `slices.SortFunc` vs old `sort.Slice`, and that map iteration is random (sorting keys is the fix), is a senior signal.

## Examples

```go
package main

import (
    "cmp"
    "fmt"
    "maps"
    "slices"
    "sort"
)

type Player struct {
    Name  string
    Score int
}

func main() {
    nums := []int{3, 1, 2}
    slices.Sort(nums) // ascending for cmp.Ordered
    fmt.Println(nums)

    players := []Player{
        {"Ada", 10},
        {"Bob", 30},
        {"Cy", 20},
    }
    slices.SortFunc(players, func(a, b Player) int {
        return cmp.Compare(b.Score, a.Score) // desc by score
    })
    fmt.Println(players)

    // Binary search on sorted slice
    i, found := slices.BinarySearch(nums, 2)
    fmt.Println(i, found)

    // Classic sort.Slice still fine
    sort.SliceStable(players, func(i, j int) bool {
        return players[i].Name < players[j].Name
    })

    m := map[string]int{"b": 2, "a": 1}
    keys := slices.Collect(maps.Keys(m))
    slices.Sort(keys)
    for _, k := range keys {
        fmt.Println(k, m[k]) // deterministic print order
    }

    clone := maps.Clone(m)
    fmt.Println(maps.Equal(m, clone))
}
```

## When to use what

| Need | Reach for |
|------|-----------|
| Sort `[]T` where `T` is ordered | `slices.Sort` |
| Custom order | `slices.SortFunc` + `cmp.Compare` |
| Stable sort | `slices.SortStableFunc` / `sort.SliceStable` |
| Search in sorted slice | `slices.BinarySearch` / `BinarySearchFunc` |
| Map keys/values/clone | `maps.Keys`, `maps.Values`, `maps.Clone` |
| Delete while ranging carefully | copy keys first, or `maps.DeleteFunc` |

## Pitfalls

- Sorting a slice of structs by a field but forgetting stable sort when ties matter.
- Assuming `maps.Keys` iteration order is sorted — **it isn’t**; sort the collected keys.
- Mutating a slice while ranging another view that shares a backing array after sorts/inserts.
- Using `sort.Interface` boilerplate in new code when `slices` is clearer.

## Interview trigger phrase

> “I’d sort with `slices.SortFunc` and `cmp.Compare`, and if I need deterministic map output I’d extract and sort the keys.”

## Exercise

Sort `[]User` by `Age` ascending, then by `Name` ascending for ties, using one `SortFunc`. Then print a `map[string]User` in key order.
