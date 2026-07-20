# Operators & Control Flow

> Go has the usual arithmetic/logical/comparison operators, `if`/`else`, `switch`, and **one loop construct: `for`**. There is no `while` or `do-while`. `switch` cases do not fall through by default. Use labels with `break`/`continue` to escape nested loops.

## Plain English

`if` can include a short statement (`if err := f(); err != nil`). Scopes matter — variables declared in that short statement live only in the `if`/`else` blocks.

`for` covers three styles: C-like (`for i := 0; i < n; i++`), condition-only (`for !done`), and infinite (`for { }`). `range` iterates slices, maps, strings, channels.

Unlike C, `switch` cases break automatically. Use `fallthrough` only when you intentionally want the next case body to run.

## Interviewer Angle

- Why only `for`? (simplicity)
- Does `switch` fall through? (no, unless `fallthrough`)
- Short statement on `if`/`switch` — scoping rules?
- Labeled `break` vs unlabeled?
- `++` / `--` are statements, not expressions — why does `f(i++)` fail?

## Go Examples

```go
// if with init statement
if n, err := strconv.Atoi(s); err != nil {
	return err
} else if n < 0 {
	return errors.New("negative")
} else {
	fmt.Println(n)
}

// for variants
for i := 0; i < 3; i++ {
	fmt.Println(i)
}
for i < 10 { // while-style
	i++
}
for { // infinite until break
	if done {
		break
	}
}

for i, v := range []string{"a", "b"} {
	fmt.Println(i, v)
}
```

```go
// Labeled break out of nested loops
Outer:
	for i := 0; i < 3; i++ {
		for j := 0; j < 3; j++ {
			if i == 1 && j == 1 {
				break Outer
			}
		}
	}
```

```go
// Operators: && || ! ; bit & | ^ &^ << >>
// No ternary operator — use if/else
// Assignment is a statement: a, b = b, a works (tuple swap)
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Expecting `switch` fallthrough like C | Silent logic bugs — Go won’t fall through |
| Using `i++` in an expression | Compile error — increment is a statement |
| Shadowing in `if` init | Outer variables unchanged after the block |
| Ranging a nil slice/map | Zero iterations — safe, not a panic |

## Trigger Phrase

> “Control flow is `if`, `for`, and `switch` — no while, no ternary, no accidental fallthrough. I use short statements carefully because of scoping, and labels when I need to break an outer loop.”

## Exercise

Rewrite a C-style `while` that scans a slice until a sentinel, and a nested loop that should stop entirely when a condition hits — using only Go’s `for` and a labeled `break`.
