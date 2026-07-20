# Interfaces

> An interface is a set of method signatures. Types satisfy interfaces **implicitly** (structural typing) — there is no `implements` keyword. If type `T` has the methods, `T` (or `*T`, per method set) is assignable to the interface.

## Plain English

Interfaces describe *behavior*, not hierarchy. Small interfaces are idiomatic (`io.Reader` has one method). Define interfaces where they’re *consumed* (call sites), not where they’re implemented — that keeps producers free of circular deps and unused methods.

A value of interface type holds a concrete dynamic value (see internals). The zero interface value is `nil`.

## Interviewer Angle

- Why implicit satisfaction?
- Where should you declare the interface?
- Small interfaces vs fat ones?
- Accept interfaces, return structs — why?

## Go Examples

```go
type Speaker interface {
	Speak() string
}

type Dog struct{ Name string }

func (d Dog) Speak() string { return d.Name + " says woof" }

func Announce(s Speaker) {
	fmt.Println(s.Speak())
}

Announce(Dog{Name: "Rex"}) // Dog never declared "implements Speaker"
```

```go
// Consumer-defined interface
package worker

type Store interface {
	Save(id string, data []byte) error
}

func Run(s Store) error { return s.Save("1", nil) }
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Fat interfaces | Hard to mock/fake; forces unused methods |
| Interfaces on the producer side prematurely | Couples packages; YAGNI |
| Exporting huge interfaces “just in case” | API noise |

## Trigger Phrase

> “Satisfaction is implicit — I define small interfaces at the consumer, and any type with the methods works without an `implements` declaration.”

## Exercise

Write a `Fetcher` interface with one method, two concrete types (`HTTPFetcher`, `FakeFetcher`), and a function that depends only on the interface. Show a test injecting the fake.
