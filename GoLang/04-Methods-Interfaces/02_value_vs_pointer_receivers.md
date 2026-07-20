# Value vs Pointer Receivers

> **Value receivers** get a copy of the value; **pointer receivers** share the original. The choice affects mutation **and** the type’s **method set**, which decides whether `T` or `*T` satisfies an interface. Consistency matters: if any method needs a pointer, often use pointer receivers for the whole set.

## Plain English

Use pointer receivers when you mutate, when the struct is large (avoid copying), or when you need to share identity. Use value receivers for small immutable-ish types (`time.Time` style) or when methods shouldn’t mutate.

Method sets (simplified):

| Type | Methods included |
|------|------------------|
| `T` | value-receiver methods on `T` |
| `*T` | value-receiver **and** pointer-receiver methods on `T` |

So `*T` can call both; `T` cannot call pointer-receiver methods (compiler may auto-take address of addressable `T` for calls, but **interface satisfaction** still uses the rule above).

## Interviewer Angle

- Why can’t `T` satisfy an interface that requires pointer methods?
- Addressable vs non-addressable values?
- Mixing value and pointer receivers on one type?
- Does Go copy the receiver on every call?

## Go Examples

```go
type Account struct {
	balance int
}

func (a Account) Balance() int { return a.balance } // value OK

func (a *Account) Deposit(n int) { a.balance += n } // must be pointer

type Bank interface {
	Balance() int
	Deposit(n int)
}

var a Account
// var b Bank = a  // compile error: Deposit has pointer receiver
var b Bank = &a   // OK — *Account method set includes both
```

```go
// Auto-addressing on call (not for interfaces)
a := Account{}
a.Deposit(10) // sugar for (&a).Deposit(10) because a is addressable

// Map elements aren't addressable:
// m[k].Deposit(1) // error if Deposit is pointer receiver
```

## Bad vs Good

```go
// Bad: mutating with value receiver — changes lost
func (a Account) Deposit(n int) { a.balance += n }

// Good
func (a *Account) Deposit(n int) { a.balance += n }
```

## Trigger Phrase

> “Pointer receivers for mutation or large structs; method sets decide interface satisfaction — `*T` has both, `T` only value methods. I keep receivers consistent on a type.”

## Exercise

Define interface `Setter { Set(int) }` and a type with pointer-receiver `Set`. Show values that do and don’t assign to `Setter`, including a map of values vs map of pointers.
