# `regexp` & `strings.Builder` — Matching & Efficient Building

> Compile regexes once; build strings with **`strings.Builder`** (or `byte` buffers) instead of `+=` in loops.

## Plain English

`regexp` implements RE2 (no catastrophic backtracking — a feature, not a bug). Always `Compile`/`MustCompile` once (package-level var) if reused. `strings.Builder` grows a byte buffer and avoids allocating a new string on every append.

## Why interviewers ask

Hot-path string building shows up in serializers and log formatters. Regex is asked for validation (“email-ish”, tokens) and for knowing RE2 limits (`\C`, backrefs unsupported).

## Examples

```go
package main

import (
    "fmt"
    "regexp"
    "strings"
)

var tokenRE = regexp.MustCompile(`^[A-Z]{3}-\d{4}$`)

func ValidToken(s string) bool {
    return tokenRE.MatchString(s)
}

func JoinCSV(fields []string) string {
    var b strings.Builder
    b.Grow(len(fields) * 8) // optional hint
    for i, f := range fields {
        if i > 0 {
            b.WriteByte(',')
        }
        b.WriteString(f)
    }
    return b.String()
}

func RedactEmails(s string) string {
    // Compile once at package level in real code
    re := regexp.MustCompile(`[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}`)
    return re.ReplaceAllString(s, "[redacted]")
}

func main() {
    fmt.Println(ValidToken("ABC-1234"))
    fmt.Println(JoinCSV([]string{"a", "b", "c"}))
    fmt.Println(RedactEmails("mail me@x.com now"))
}
```

## Submatch extraction

```go
re := regexp.MustCompile(`(?P<user>\w+)@(?P<host>[\w.]+)`)
m := re.FindStringSubmatch("ada@ex.com")
names := re.SubexpNames()
for i, name := range names {
    if i == 0 || name == "" {
        continue
    }
    fmt.Println(name, m[i])
}
```

## Pitfalls

- Compiling regex **inside a hot loop** — huge CPU waste.
- Expecting PCRE features (backreferences, lookaround) — RE2 won’t.
- Using `+=` in a loop over thousands of pieces — quadratic-ish allocation behavior; use `Builder`.
- `Builder` is not safe for concurrent writes without external sync.
- Prefer `strings.Contains`/`HasPrefix`/`Cut` when you don’t need a regex.

## Interview trigger phrase

> “I’d `MustCompile` once at package scope, prefer plain `strings` helpers when enough, and use `strings.Builder` with `Grow` for hot concatenation.”

## Exercise

Implement `func ExpandTemplate(tmpl string, vars map[string]string) string` replacing `${key}` placeholders using one compiled regexp and a `Builder`. Reject unknown keys.
