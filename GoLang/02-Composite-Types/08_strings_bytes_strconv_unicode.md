# `strings` / `bytes` / `strconv` / `unicode`

> The stdlib splits text work across packages: **`strings`** for string utilities, **`bytes`** for the same ideas on `[]byte`, **`strconv`** for parsing/formatting basic types, **`unicode`** for code-point classification and case mapping.

## Plain English

Reach for `strings.Contains`, `HasPrefix`, `Split`, `Join`, `ReplaceAll`, `TrimSpace`, `Builder` (efficient concatenation). Prefer `strings.Builder` or `bytes.Buffer` over `s +=` in loops.

`bytes` mirrors many `strings` APIs when you already have binary data — avoids bouncing through `string`.

`strconv`: `Atoi`/`Itoa`, `ParseInt`/`FormatInt`, `ParseBool`, `FormatFloat` — always check errors from parse functions.

`unicode`: `IsLetter`, `IsDigit`, `ToLower(r rune)` — works on runes, not whole strings (`strings.ToLower` uses Unicode case mapping for strings).

## Interviewer Angle

- Efficient string building?
- `strconv` vs `fmt.Sprintf` for numbers? (`strconv` usually faster/cleaner for simple cases)
- When `bytes` over `strings`?
- UTF-8 validation? (`utf8.ValidString`)

## Go Examples

```go
import (
	"bytes"
	"strconv"
	"strings"
	"unicode"
	"unicode/utf8"
)

s := "  Go,Rust,Go  "
parts := strings.Split(strings.TrimSpace(s), ",")
joined := strings.Join(parts, "|")

var b strings.Builder
b.Grow(64)
for _, p := range parts {
	b.WriteString(p)
}
out := b.String()

n, err := strconv.Atoi("42")
txt := strconv.Itoa(n)

buf := []byte("hello")
fmt.Println(bytes.HasPrefix(buf, []byte("he")))

r := 'É'
fmt.Println(unicode.IsLetter(r), unicode.ToLower(r))
fmt.Println(utf8.ValidString("Go"))
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| `+=` in a loop | O(n²) allocations |
| Ignoring `strconv` errors | Silent zero values |
| `strings.Split` empty edge | `Split("", ",")` → `[""]` one element |
| Byte APIs on text | Can split runes — use rune-aware helpers |

## Trigger Phrase

> “I use `strings`/`bytes` for manipulation, `strconv` for numbers/bools, `unicode`/`utf8` for code points — and `strings.Builder` when concatenating in a loop.”

## Exercise

Implement `func CSVEscape(fields []string) string` that joins fields with commas, quotes fields containing commas, and builds the result with `strings.Builder` (no `+=` in a loop).
