# `reflect` — Runtime Reflection

> Inspect and manipulate types/values at runtime; **powerful, slow, easy to misuse** — prefer interfaces/generics first.

## Plain English

`reflect` lets you ask “what type is this?” and “set this field by name?” when you don’t know the type at compile time — serializers, DI containers, copy libraries, ORM-ish mapping. The cost is runtime overhead, panic-prone APIs, and loss of static checking.

## Why interviewers ask 🔴

They want judgment: when reflection is justified (e.g. implementing something like `encoding/json`) vs when a small interface or generics is clearer. Know `Type` vs `Value`, addressability, and that exported fields only are settable.

## Minimal mental model

```go
t := reflect.TypeOf(x)   // type metadata
v := reflect.ValueOf(x)  // value handle

// To mutate, you need a pointer and Elem():
v = reflect.ValueOf(&x).Elem()
```

## Examples

```go
package main

import (
    "fmt"
    "reflect"
)

type User struct {
    Name string `json:"name"`
    age  int    // unexported — not settable via reflect from another package
}

func SetExportedString(ptr any, field, value string) error {
    v := reflect.ValueOf(ptr)
    if v.Kind() != reflect.Pointer || v.IsNil() {
        return fmt.Errorf("need non-nil pointer")
    }
    v = v.Elem()
    if v.Kind() != reflect.Struct {
        return fmt.Errorf("need struct")
    }
    f := v.FieldByName(field)
    if !f.IsValid() || !f.CanSet() || f.Kind() != reflect.String {
        return fmt.Errorf("cannot set %s", field)
    }
    f.SetString(value)
    return nil
}

func TagMap(v any) map[string]string {
    t := reflect.TypeOf(v)
    if t.Kind() == reflect.Pointer {
        t = t.Elem()
    }
    out := map[string]string{}
    for i := 0; i < t.NumField(); i++ {
        f := t.Field(i)
        out[f.Name] = f.Tag.Get("json")
    }
    return out
}

func main() {
    u := User{Name: "Ada"}
    _ = SetExportedString(&u, "Name", "Grace")
    fmt.Println(u.Name)
    fmt.Println(TagMap(u))
}
```

## Prefer interfaces / generics

```go
// Often better than reflect:
type Stringer interface{ String() string }

func PrintAll[T fmt.Stringer](xs []T) {
    for _, x := range xs {
        fmt.Println(x.String())
    }
}
```

## Pitfalls

- `CanSet() == false` because you passed a non-pointer or the field is unexported.
- Huge switch-on-`Kind` tables that reimplement the type system — maintenance trap.
- Performance: reflection can be **10–100×** slower than direct code; cache `Type` lookups if you must.
- Panics on mismatched `Set` kinds — validate before setting.
- Using reflect to paper over poor API design.

## Interview trigger phrase

> “I’d reach for interfaces or generics first; if I need reflect for tags or a generic mapper, I’d confine it to a small package, cache types, and check `CanSet`.”

## Exercise

Write `func MustCopyExported(dst, src any)` that copies identically named exported fields of the same kind from `src` to `dst` (both pointers to structs). List three cases where it should return an error instead of panicking.
