# `io` / `bufio` — Readers, Writers & Buffering

> Stream bytes through **`io.Reader` / `io.Writer`**; use **`bufio`** to cut syscalls and read lines efficiently.

## Plain English

Go’s I/O is interface-first. Anything that can produce bytes is a `Reader`; anything that can accept bytes is a `Writer`. `io.Copy` connects them. `bufio` wraps either side with an in-memory buffer so you don’t do a kernel call per byte.

## Why interviewers ask ⭐

Production code is streams: HTTP bodies, files, gzip, pipes. Seniors design APIs around `io.Reader`/`Writer` instead of `[]byte` everywhere, and they know when buffering matters.

## Core interfaces

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

// Composed:
type ReadCloser interface {
    Reader
    Closer
}
```

`io.EOF` means “no more data” — usually **not** a failure for the caller of `Copy`/`ReadAll` when expected at end-of-stream.

## Examples

```go
package main

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "strings"
)

func copyFile(dst, src string) error {
    in, err := os.Open(src)
    if err != nil {
        return err
    }
    defer in.Close()

    out, err := os.Create(dst)
    if err != nil {
        return err
    }
    defer out.Close()

    _, err = io.Copy(out, in) // buffered internally in chunks
    return err
}

func readLines(r io.Reader) ([]string, error) {
    sc := bufio.NewScanner(r)
    // Optional: raise token size for long lines
    // sc.Buffer(make([]byte, 0, 64*1024), 1024*1024)
    var lines []string
    for sc.Scan() {
        lines = append(lines, sc.Text())
    }
    return lines, sc.Err()
}

func main() {
    r := strings.NewReader("hello\nworld\n")
    lines, _ := readLines(r)
    fmt.Println(lines)

    var buf strings.Builder
    bw := bufio.NewWriter(&buf)
    fmt.Fprintln(bw, "buffered write")
    bw.Flush() // must Flush or data may stay in buffer
    fmt.Print(buf.String())
}
```

## Accept interfaces, return concrete

```go
// Good API: callers can pass files, network, bytes.Buffer, gzip, etc.
func CountWords(r io.Reader) (int, error) { /* ... */ }

// Avoid forcing []byte if the source is a stream — loads everything into memory.
```

## Pitfalls

- Forgetting `Flush()` on `bufio.Writer` / `bufio.NewWriterSize`.
- Ignoring `sc.Err()` after `Scanner` loop (e.g. token too long).
- Treating `io.EOF` from `Read` as a hard error when draining a stream.
- Calling `Read` in a loop without handling short reads (`n > 0 && err == io.EOF` is valid).
- Using `ioutil` — deprecated; prefer `io` and `os` (Go 1.16+).

## Interview trigger phrase

> “I’d take an `io.Reader`, wrap hot paths with `bufio`, use `io.Copy` to avoid buffering the whole payload in memory, and always `Flush` writers.”

## Exercise

Write `func TeeLines(r io.Reader, w io.Writer) error` that copies each line to `w` using `bufio.Scanner` and `bufio.Writer`, then flushes. What happens on a 10MB line with default scanner limits?
