# Interface Composition

> Interfaces can **embed** other interfaces. The result is the union of method sets. `io.ReadWriter` embeds `Reader` and `Writer`. Composition keeps interfaces small and reusable.

## Plain English

Instead of one fat interface, build larger ones from small pieces:

```go
type ReadWriter interface {
	Reader
	Writer
}
```

A type that has both `Read` and `Write` satisfies `ReadWriter` automatically. This mirrors how embedding works for structs, but for method sets only — no fields.

Prefer composing std interfaces rather than reinventing `Read`/`Write`/`Close`.

## Interviewer Angle

- Show `io.ReadWriteCloser` mental model
- Embedding interfaces vs listing methods?
- Can you embed and add methods?
- Interface segregation connection?

## Go Examples

```go
type Reader interface {
	Read(p []byte) (n int, err error)
}
type Writer interface {
	Write(p []byte) (n int, err error)
}
type Closer interface {
	Close() error
}

type ReadWriteCloser interface {
	Reader
	Writer
	Closer
}

// Equivalent explicit form
type ReadWriteCloser2 interface {
	Read(p []byte) (n int, err error)
	Write(p []byte) (n int, err error)
	Close() error
}
```

```go
// Local composition for your app
type UserStore interface {
	Finder
	Saver
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Composing into huge interfaces | Forces mocks to implement everything |
| Duplicating std method signatures slightly wrong | Types fail to satisfy `io.Reader` |
| Exporting composed interfaces unused by consumers | Premature abstraction |

## Trigger Phrase

> “I compose small interfaces into larger ones — like `io.ReadWriter` — so types satisfy only the behaviors they need, and consumers ask for the smallest set.”

## Exercise

Define `Scanner` (`Scan() bool`, `Text() string`) and `Closer`, compose `ScanCloser`, and implement it with a struct that wraps `bufio.Scanner` and an `io.Closer`.
