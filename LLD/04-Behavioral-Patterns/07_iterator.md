# Iterator

> Provide a way to **access elements sequentially** without exposing the collection’s internal representation.

## Plain English

Callers walk items with `has_next` / `next` (or `for ... range`) without knowing if the structure is an array, tree, or graph. Encapsulates traversal.

## Why seniors get asked this

Custom collections, tree inorder walks, paginated APIs. Interviewers care that internals stay hidden and multiple iterators can coexist.

## Real-world analogy

A **TV remote channel-up**: you flip channels without knowing how the cable box stores the channel list.

## Example

### Python

```python
from typing import Iterator


class Playlist:
    def __init__(self, songs: list[str]) -> None:
        self._songs = songs

    def __iter__(self) -> Iterator[str]:
        return iter(self._songs)  # hide list details from callers


class SkipIterator:
    """Custom iterator: yield every other song."""

    def __init__(self, songs: list[str]) -> None:
        self._songs = songs
        self._i = 0

    def __iter__(self) -> "SkipIterator":
        return self

    def __next__(self) -> str:
        if self._i >= len(self._songs):
            raise StopIteration
        song = self._songs[self._i]
        self._i += 2
        return song


for s in Playlist(["a", "b", "c"]):
    print(s)

for s in SkipIterator(["a", "b", "c", "d"]):
    print("skip", s)
```

### Go

```go
type Playlist struct {
    songs []string
}

// Idiomatic Go: iterate via range over a returned slice copy,
// or expose an iterator-style Next method for custom orders.

func (p Playlist) All() []string {
    out := make([]string, len(p.songs))
    copy(out, p.songs)
    return out // caller can't mutate internals
}

type SkipIter struct {
    songs []string
    i     int
}

func (it *SkipIter) Next() (string, bool) {
    if it.i >= len(it.songs) {
        return "", false
    }
    s := it.songs[it.i]
    it.i += 2
    return s, true
}
```

## When to use

- Multiple traversal styles (inorder / preorder) over the same structure.
- Internals must stay private (linked list, tree, graph).
- Lazy / streaming traversal of large datasets.

## When not to use / pitfalls

- Language `for` / `range` over a slice is enough for simple lists — don’t invent ceremony.
- Mutating the collection while iterating → define fail-fast or snapshot semantics.
- Exposing the backing array “for convenience” defeats encapsulation.
- In Go 1.23+, `iter.Seq` exists; older code often uses `Next() (T, bool)`.

## Interview trigger phrase

> “I’d expose an iterator for inorder traversal so callers never touch the BST’s left/right pointers.”

## Exercise

A binary tree should support inorder iteration.

1. Sketch an iterator API (`Next() (value, ok)`).
2. Why not return the root node to callers?
3. What goes wrong if the tree mutates mid-iteration?
