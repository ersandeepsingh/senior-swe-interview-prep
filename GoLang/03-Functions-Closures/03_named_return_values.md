# Named Return Values

> Result parameters can be named in the signature: `func f() (n int, err error)`. They are declared as locals initialized to zero values. A **naked return** (`return`) returns them as currently set. Useful for deferred cleanup that amends `err`; easy to misuse.

## Plain English

Named results document intent (`n` bytes written, `err`) and let `defer` closures modify what will be returned — classic pattern when you need to wrap an error on the way out or set `n = 0` on failure.

Naked returns in long functions hurt readability: the reader must hunt for assignments. Prefer explicit `return n, err` unless the function is tiny or defer-driven.

Shadowing is a common bug: `err := something` inside a block creates a new `err` that doesn’t update the named result.

## Interviewer Angle

- When are named returns worth it?
- How does defer interact with named results?
- Naked return pitfalls?
- Shadowing named `err`?

## Go Examples

```go
func ReadAll(r io.Reader) (b []byte, err error) {
	defer func() {
		if err != nil {
			err = fmt.Errorf("ReadAll: %w", err)
		}
	}()
	return io.ReadAll(r) // assigns to named b, err
}
```

```go
func tricky() (err error) {
	defer func() { fmt.Println("deferred err:", err) }()
	if err := fail(); err != nil { // shadows named err!
		return err // naked return would return nil named err — explicit saves you here
	}
	return nil
}
```

## Bad vs Good

```go
// Bad: naked returns in a long function
func Process() (out Result, err error) {
	// ... 40 lines mutating out/err ...
	return
}

// Good: named for defer amend, explicit returns
func Process() (out Result, err error) {
	defer func() {
		if err != nil {
			metrics.Failure()
		}
	}()
	out, err = step1()
	if err != nil {
		return out, err
	}
	return step2(out)
}
```

## Trigger Phrase

> “Named returns are zero-initialized locals — great for defer that amends `err`, dangerous with shadowing and naked returns in long functions.”

## Exercise

Write a function with named `(n int64, err error)` that copies from a reader, uses `defer` to log final `n` and wrap `err`, and demonstrate a shadowing bug then fix it.
