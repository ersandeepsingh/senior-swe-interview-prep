# `encoding/json` — Marshal & Unmarshal

> Encode/decode JSON with struct tags; control omit-empty, custom types, and streaming via `Decoder`/`Encoder`.

## Plain English

JSON in Go is almost always struct-tag driven: `json:"name,omitempty"`. Marshal turns Go → JSON; Unmarshal JSON → Go. Unknown fields are ignored by default; missing fields keep zero values.

## Why interviewers ask ⭐

Every backend talks JSON. Seniors know tags, `omitempty` pitfalls (false/`0`/`""` omitted), custom `MarshalJSON`/`UnmarshalJSON`, and streaming large payloads instead of `json.Unmarshal` on a giant `[]byte`.

## Struct tags

```go
type User struct {
    ID        int64  `json:"id"`
    Email     string `json:"email"`
    Password  string `json:"-"`                        // never serialized
    Nickname  string `json:"nickname,omitempty"`
    CreatedAt time.Time `json:"created_at"`
}
```

| Tag piece | Effect |
|-----------|--------|
| `name` | JSON key |
| `omitempty` | skip zero value |
| `-` | ignore field |
| `,string` | encode number/bool as JSON string |

## Examples

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "log"
    "strings"
)

type Product struct {
    SKU   string  `json:"sku"`
    Price float64 `json:"price,omitempty"`
    Tags  []string `json:"tags,omitempty"`
}

func main() {
    p := Product{SKU: "A1", Price: 0, Tags: nil}
    b, _ := json.Marshal(p)
    fmt.Println(string(b)) // {"sku":"A1"} — price 0 and nil slice omitted

    var out Product
    if err := json.Unmarshal([]byte(`{"sku":"B2","price":9.5,"extra":true}`), &out); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("%+v\n", out) // Extra ignored

    // Streaming (NDJSON / large body)
    dec := json.NewDecoder(strings.NewReader(`{"sku":"C3"}{"sku":"D4"}`))
    for {
        var item Product
        if err := dec.Decode(&item); err != nil {
            break
        }
        fmt.Println(item.SKU)
    }

    var buf bytes.Buffer
    enc := json.NewEncoder(&buf)
    enc.SetIndent("", "  ")
    _ = enc.Encode(Product{SKU: "E5", Price: 1})
    fmt.Print(buf.String())
}
```

## Custom marshalers

```go
type Cent int64

func (c Cent) MarshalJSON() ([]byte, error) {
    // store as decimal dollars string, etc.
    return json.Marshal(fmt.Sprintf("%.2f", float64(c)/100))
}
```

Use when the JSON shape doesn’t map 1:1 to your domain type.

## Pitfalls

- Unmarshaling into a **non-pointer** / nil map/slice destination incorrectly — always pass a pointer to the value you want filled.
- `omitempty` on `false`, `0`, `""`, `nil` slice/map — often surprises API clients; use pointers (`*bool`) when you need “absent vs false.”
- Decoding into `map[string]interface{}` → numbers become `float64`.
- Ignoring `json.Decoder.DisallowUnknownFields()` when you need strict schemas.
- Embedding structs and forgetting promoted fields also get tagged/serialized.

## Interview trigger phrase

> “I’d model the DTO with tags, use pointers for tri-state fields, stream with `Decoder` for large bodies, and reach for custom marshalers only when the wire format disagrees with the domain type.”

## Exercise

Design a `Config` struct where `debug` must distinguish “missing” vs `false` in JSON, and `password` must never appear in marshaled output. Show the tags and a round-trip test sketch.
