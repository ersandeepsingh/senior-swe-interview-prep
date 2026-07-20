# Basic Types

> Go’s predeclared types: integers (`int`, `int8`…`int64`, unsigned forms), floats (`float32`/`float64`), `bool`, `byte` (alias of `uint8`), `rune` (alias of `int32`, Unicode code point), and `string` (immutable UTF-8 bytes). `int`/`uint` size is platform-dependent (32 or 64 bit).

## Plain English

Pick fixed-size types (`int64`, `uint32`) when the wire format, DB column, or protocol demands it. Use plain `int` for most counts and indexes — it’s the natural size for the machine.

`byte` is for raw binary. `rune` is for a single Unicode code point (not a “character” in the grapheme sense — emoji can be multiple runes). `string` holds UTF-8 bytes; indexing a string gives a byte, not a rune.

Complex numbers (`complex64`/`complex128`) exist but almost never appear in interviews.

## Interviewer Angle

- Size of `int` on 64-bit? (usually 64 bits, but say “platform-dependent”)
- `byte` vs `rune`?
- Is `string` mutable? (no)
- Why prefer `int64` for timestamps / money-ish IDs over `int`?
- Default type of a numeric constant? (untyped — adopts type when used)

## Go Examples

```go
var (
	n   int     = 10
	n64 int64   = 10
	f   float64 = 3.14
	ok  bool    = true
	b   byte    = 'A'   // 65
	r   rune    = '世'  // Unicode code point
	s   string  = "Go"
)

// Untyped constant adapts
const Answer = 42
var x int32 = Answer
var y float64 = Answer
```

```go
s := "Go世界"
fmt.Println(len(s))                    // byte length, not rune count
fmt.Println([]rune(s))                 // code points
fmt.Println(utf8.RuneCountInString(s)) // number of runes
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Assuming `int` is always 64-bit | Breaks on 32-bit / wasm assumptions |
| Using `int` for JSON IDs from JS | JS loses precision > 2^53 — use `string` or careful `int64` |
| Indexing string as characters | `s[i]` is a byte; multi-byte UTF-8 breaks naive loops |
| Mixing signed/unsigned carelessly | Comparison and conversion surprises |

## Trigger Phrase

> “`int` is platform-sized; I use fixed widths at API boundaries. `byte` is raw data, `rune` is a code point, and `string` is immutable UTF-8 — `len` counts bytes.”

## Exercise

Given `s := "café"`, predict `len(s)`, the result of ranging with `for i, r := range s`, and what `s[2]` returns. Explain each.
