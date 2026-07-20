# Common Std Interfaces

> Memorize the method sets interviewers expect: **`error`**, **`fmt.Stringer`**, **`io.Reader` / `Writer` / `Closer`**, **`sort.Interface`**, plus recognition of `http.Handler`, `context.Context`, and `json.Marshaler`. Implementing these plugs your types into the ecosystem.

## Plain English

| Interface | Methods | Why it matters |
|-----------|---------|----------------|
| `error` | `Error() string` | Idiomatic failure |
| `fmt.Stringer` | `String() string` | `fmt`, logging |
| `io.Reader` | `Read([]byte) (int, error)` | Files, net, http bodies |
| `io.Writer` | `Write([]byte) (int, error)` | Same pipeline |
| `io.Closer` | `Close() error` | Resource cleanup |
| `sort.Interface` | `Len`, `Less`, `Swap` | Custom sorting |
| `http.Handler` | `ServeHTTP(ResponseWriter, *Request)` | Servers |
| `json.Marshaler` | `MarshalJSON() ([]byte, error)` | Custom JSON |

`Read`/`Write` contracts: return `n` bytes processed; `err == io.EOF` means end; never assume full buffer filled in one call.

## Interviewer Angle

- Correct `Read` loop until EOF?
- Why `String()` shouldn’t be heavy?
- `http.HandlerFunc` adapter pattern?
- Implementing `sort.Interface` vs `slices.SortFunc`?

## Go Examples

```go
type Cent int

func (c Cent) String() string {
	return fmt.Sprintf("$%.2f", float64(c)/100)
}

type ByAge []User
func (a ByAge) Len() int           { return len(a) }
func (a ByAge) Less(i, j int) bool { return a[i].Age < a[j].Age }
func (a ByAge) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }

// Reader copy
n, err := io.Copy(dst, src)
```

```go
type helloHandler struct{}

func (helloHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	io.WriteString(w, "hello")
}
```

## Gotchas

| Gotcha | Why it hurts |
|--------|----------------|
| Ignoring short writes/reads | Corrupt data |
| `Close` errors ignored | Resource / flush bugs |
| `Error()` returning unstable text | Breaks `errors.Is` users who match strings |

## Trigger Phrase

> “I know the core std interfaces by method set — especially `error`, `Stringer`, `Reader`/`Writer`, and `Handler` — so my types plug into `io`, `fmt`, `net/http`, and sorting without custom glue.”

## Exercise

Implement a type that is both `io.Reader` and `fmt.Stringer`, wrapping a string, and use `io.Copy` to copy it to `os.Stdout`.
