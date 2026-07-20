# Range Copies Values

> `for _, v := range xs` gives a **copy** of each element. Mutating `v` (or fields of a copied struct) does **not** update the slice/array.

## Plain English

Range yields values (or keys). For slices of structs, `v` is a copy of the element. `v.Field = x` changes the copy. To mutate in place, use the index (`xs[i].Field = x`) or range over pointers (`[]*T`).

## Why interviewers ask 🟡⭐

Looks correct, silently does nothing — classic debug grill.

## Broken

```go
type User struct{ Name string }

func broken() {
    users := []User{{"Ada"}, {"Bob"}}
    for _, u := range users {
        u.Name = strings.ToUpper(u.Name) // mutates copy only
    }
    fmt.Println(users) // [{Ada} {Bob}]
}
```

## Fixed

```go
func fixedIndex() {
    users := []User{{"Ada"}, {"Bob"}}
    for i := range users {
        users[i].Name = strings.ToUpper(users[i].Name)
    }
    fmt.Println(users) // [{ADA} {BOB}]
}

func fixedPointers() {
    users := []*User{{"Ada"}, {"Bob"}}
    for _, u := range users {
        u.Name = strings.ToUpper(u.Name) // u is copy of pointer; same referent
    }
}
```

## Related: maps

```go
m := map[string]*User{"a": {"Ada"}}
for _, u := range m {
    u.Name = "X" // ok if values are pointers
}

m2 := map[string]User{"a": {"Ada"}}
for k, u := range m2 {
    u.Name = "X"       // useless
    m2[k] = User{"X"}  // must write back (or store *User)
}
```

You also **cannot** take the address of a map element (`&m[k]` is illegal).

## Pitfalls

- Large struct copies in tight range loops — prefer indices or pointers for performance too.
- Assuming range over array of structs updates the array — same copy rule.
- Mixing with goroutines: `go func() { use(u) }` still needs the capture fix.

## Interview trigger phrase

> “Range yields a copy; I’d mutate via index or store pointers if I need in-place updates.”

## Exercise

Given `[]Player` with `Score int`, write two versions that add +1 to every score: index-based and pointer-based. Which would you choose for a 1M-element hot path and why?
