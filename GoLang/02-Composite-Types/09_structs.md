# Structs

> A struct is a typed collection of fields. Fields may have **tags** (metadata for `encoding/json`, DB mappers, validators). Structs are values: assignment and function args copy all fields unless you use pointers. Structs are comparable with `==` only if all fields are comparable.

## Plain English

Define with `type User struct { Name string; Age int }`. Zero value: all fields zeroed. Literals: `User{Name: "ada"}` (keyed — preferred) or positional (fragile).

Tags are raw strings on fields: `` `json:"name,omitempty"` ``. They don’t change the type; reflection-based packages read them.

Unexported fields (`id`) won’t be set from other packages via literals and won’t marshal with default `encoding/json` from outside.

## Interviewer Angle

- Value vs pointer receivers later — but when pass struct by pointer?
- Are structs comparable?
- What does `omitempty` do?
- Anonymous fields vs named? (embedding — next topic)
- Empty struct `struct{}` size and use? (0 bytes — sets, signals)

## Go Examples

```go
type User struct {
	Name  string `json:"name"`
	Email string `json:"email,omitempty"`
	age   int    // unexported
}

u := User{Name: "Ada", Email: "ada@example.com"}
u2 := u // copy
u2.Name = "Grace"
fmt.Println(u.Name) // Ada

type Pair struct{ A, B int }
fmt.Println(Pair{1, 2} == Pair{1, 2}) // true

// Not comparable if a field is a slice/map
type Bad struct{ Tags []string }
// Bad{} == Bad{} // compile error
```

```go
type Empty struct{}
var set = map[string]struct{}{}
set["x"] = struct{}{}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Positional literals across packages | Break when fields reorder/add |
| Large struct passed by value | Hidden copies — use `*T` for big/mutable |
| Comparing structs with float NaNs | `NaN != NaN` |
| Expecting tags to enforce types | Tags are advisory metadata |

## Trigger Phrase

> “Structs are field groups with value semantics; I prefer keyed literals, use tags for encoding, and remember comparability requires all fields comparable.”

## Exercise

Define a `Config` struct with JSON tags (one optional field), write `Marshal`/`Unmarshal` round-trip code, and explain what happens to an unexported field during marshal.
