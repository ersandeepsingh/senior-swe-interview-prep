# Program Structure

> A Go program is a tree of **packages**. Execution starts at `func main` in `package main`. Names starting with a capital letter are **exported** (visible outside the package); lowercase names are package-private.

## Plain English

Every `.go` file begins with `package <name>`. Files in the same directory share that package and can see each other’s unexported symbols. Other packages only see exported identifiers (`User`, `NewClient`) — capitalization *is* the access control.

Imports bring other packages in. Unused imports are a compile error. `init` functions (if any) run before `main`, in dependency order — use sparingly.

## Interviewer Angle

- What does capitalization control? (export / visibility)
- Can two files in one folder have different package names? (no — same directory = one package)
- What’s special about `package main`? (builds an executable; needs `func main`)
- Internal packages? (`internal/` directory: importable only by ancestors)
- Does Go have `public`/`private` keywords? (no — capitalization)

## Go Examples

```go
// file: cmd/app/main.go
package main

import (
	"fmt"

	"example.com/shop/user" // import path, not package folder alone
)

func main() {
	u := user.New("ada") // New is exported
	fmt.Println(u.Name)  // Name is exported
	// fmt.Println(u.id) // compile error: unexported
}
```

```go
// file: user/user.go
package user

type User struct {
	Name string // exported field
	id   int    // unexported field
}

func New(name string) User { // exported constructor
	return User{Name: name, id: nextID()}
}

func nextID() int { // unexported helper
	return 1
}
```

```go
// Blank import: run package init for side effects (e.g. DB driver registration).
import _ "github.com/lib/pq"
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Exporting too much | Leaks internals; hard to change later |
| `init()` with hidden magic | Hard to test and reason about startup |
| Confusing import path with package name | Last path segment often matches, but `package` clause is authoritative |
| Circular imports | Compile error — redesign package boundaries |

## Trigger Phrase

> “Visibility is capitalization: exported means other packages can use it. `package main` + `func main` is the executable entry; everything else is a library package.”

## Exercise

Sketch a tiny module with packages `main`, `account`, and `account/internal/hash`. Show which symbols `main` can call, and explain why `main` cannot import a peer’s `internal` package from elsewhere in the module tree.
