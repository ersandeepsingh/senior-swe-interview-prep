# Law of Demeter (LoD)

> Only talk to your **immediate friends** — not to strangers reached through friends.

## Plain English

Avoid long chains like `order.getCustomer().getAddress().getZip()`. That code knows too much about other objects’ guts. If the structure changes, everything breaks.

**Friends usually means:** yourself, your fields, objects you created, or parameters passed to you — not “whatever you can reach by digging.”

## Why seniors get asked this

God-chain navigation shows weak encapsulation. Interviewers prefer: ask a collaborator to do the work (`order.shippingZip()`).

## Bad: train wreck / reach-through

### Python

```python
class Zip:
    def __init__(self, code: str):
        self.code = code


class Address:
    def __init__(self, zip_: Zip):
        self.zip = zip_


class Customer:
    def __init__(self, address: Address):
        self.address = address


class Order:
    def __init__(self, customer: Customer):
        self.customer = customer


def label_for(order: Order) -> str:
    # knows Order → Customer → Address → Zip
    return order.customer.address.zip.code
```

### Go

```go
type Zip struct{ Code string }
type Address struct{ Zip Zip }
type Customer struct{ Address Address }
type Order struct{ Customer Customer }

func LabelFor(o Order) string {
    return o.Customer.Address.Zip.Code // train wreck
}
```

## Good: ask, don’t dig

Push the knowledge next to the data. Callers depend on a stable question (“what’s the shipping zip?”), not the path.

### Python

```python
class Address:
    def __init__(self, zip_code: str):
        self._zip_code = zip_code

    def zip_code(self) -> str:
        return self._zip_code


class Customer:
    def __init__(self, address: Address):
        self._address = address

    def shipping_zip(self) -> str:
        return self._address.zip_code()


class Order:
    def __init__(self, customer: Customer):
        self._customer = customer

    def shipping_zip(self) -> str:
        return self._customer.shipping_zip()


def label_for(order: Order) -> str:
    return order.shipping_zip()  # one hop
```

### Go

```go
type Address struct{ zip string }
func (a Address) ZipCode() string { return a.zip }

type Customer struct{ address Address }
func (c Customer) ShippingZip() string { return c.address.ZipCode() }

type Order struct{ customer Customer }
func (o Order) ShippingZip() string { return o.customer.ShippingZip() }

func LabelFor(o Order) string {
    return o.ShippingZip()
}
```

## Balance (don’t go crazy)

LoD is a guideline. A DTO / JSON map with `order["customer"]["zip"]` in a serializer is fine. Don’t create 15 wrapper methods for a throwaway script — use judgment (KISS).

## Interview trigger phrase

> “I’d avoid reach-through chains; `Order` can expose `shipping_zip` so callers don’t couple to the object graph.”

## Exercise

`Car.engine.fuelInjector.spray()` is called from `Driver.drive()`.

1. What’s wrong for maintainability?
2. Redesign so `Driver` only talks to `Car` (or `Car` to `Engine`).
3. Write a 10-line Python or Go sketch of the fixed call path.
