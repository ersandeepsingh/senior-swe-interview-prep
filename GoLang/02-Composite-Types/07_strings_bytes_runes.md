# Strings, Bytes, Runes

> A `string` is an immutable sequence of bytes, conventionally UTF-8. `[]byte` is a mutable byte slice. `rune` is a Unicode code point (`int32`). Indexing a string yields a **byte**; `range` over a string yields **runes** (and byte offsets).

## Plain English

Go strings can hold any bytes, but most APIs assume UTF-8. Because strings are immutable, conversion `[]byte(s)` and `string(b)` **copy** data (compiler may optimize some cases, but don’t rely on zero-copy in application code).

`len(s)` is byte length. Character count ≈ `utf8.RuneCountInString(s)` (still not grapheme clusters — 👨‍👩‍👧‍👦 is multiple runes).

`[]rune(s)` materializes code points; useful for random access by rune index (expensive if done naively on large strings).

## Interviewer Angle

- Why is `s[i]` not always a full character?
- Cost of `string` ↔ `[]byte`?
- How does `range` on string work?
- Immutability — can you change `s[0]`? (no)

## Go Examples

```go
s := "Go世界"
fmt.Println(len(s)) // 8 bytes: G o + 3-byte 世 + 3-byte 界

for i := 0; i < len(s); i++ {
	fmt.Printf("%d: %x\n", i, s[i]) // bytes
}

for i, r := range s {
	fmt.Printf("%d: %c\n", i, r) // i is byte index; r is rune
}

b := []byte(s) // copy, mutable
b[0] = 'g'
s2 := string(b)

runes := []rune(s)
fmt.Println(string(runes[2])) // 世 — index by code point
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Truncating with `s[:n]` mid-rune | Invalid UTF-8 / broken text |
| Assuming `len` = character count | Wrong for non-ASCII |
| Heavy `string([]byte)` in hot loops | Allocations — use `bytes` or `strings.Builder` |

## Trigger Phrase

> “Strings are immutable UTF-8 bytes; `len` and indexing are byte-oriented, `range` walks runes. I convert to `[]rune` only when I need code-point indexing, and I avoid mid-rune slicing.”

## Exercise

Write `func SafePrefix(s string, maxRunes int) string` that returns at most `maxRunes` code points without splitting a rune, and never panics on invalid UTF-8 (document your choice: replace or stop).
