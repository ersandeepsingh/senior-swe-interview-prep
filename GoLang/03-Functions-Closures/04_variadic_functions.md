# Variadic Functions

> A variadic parameter `...T` gathers zero or more arguments into a `[]T` inside the function. It must be the **last** parameter. Pass an existing slice with `slice...` (spread).

## Plain English

`fmt.Println(a, b, c)` is variadic. Inside `Println`, those args are a slice. You can call with no trailing args — you get an empty (non-nil? actually empty) slice of length 0.

`append` is the built-in everyone knows: `append(s, elems...)`.

Spreading: `fmt.Println(parts...)` where `parts` is `[]string` — types must match.

## Interviewer Angle

- Must `...T` be last?
- Difference between passing nothing vs nil slice vs empty slice?
- `append` signature mental model?
- Can you have multiple variadic params? (no)

## Go Examples

```go
func Max(nums ...int) (int, error) {
	if len(nums) == 0 {
		return 0, errors.New("empty")
	}
	m := nums[0]
	for _, n := range nums[1:] {
		if n > m {
			m = n
		}
	}
	return m, nil
}

Max(1, 5, 3)
Max() // len==0

vals := []int{1, 5, 3}
Max(vals...) // spread
```

```go
func Log(level string, msg string, kv ...any) {
	// kv is []any
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Forgetting `...` when passing a slice | Passes one argument of type `[]T` — type error or wrong overload |
| Mutating the variadic slice | May alias caller’s slice if they spread it — don’t assume exclusive ownership without copying |
| Variadic `any` overuse | Loses type safety — prefer generics or concrete types |

## Trigger Phrase

> “`...T` is a trailing slice of args; I spread with `slice...`, and I treat the variadic slice like any other slice for aliasing and length checks.”

## Exercise

Implement `func Concat(sep string, parts ...string) string` using `strings.Builder`, and show calls with zero parts, many parts, and a spread slice.
