# Proxy

> Provide a **stand-in** for another object to control access — lazy creation, caching, auth, remote calls — while exposing the same interface.

## Plain English

Clients talk to a proxy that looks like the real service. The proxy decides *when/whether/how* to talk to the real thing: load on first use, check permissions, cache results, or forward over the network.

## Why seniors get asked this

Lazy image loading, access-control wrappers, virtual proxies for heavy objects. Interviewers want you to distinguish Proxy from Decorator (control/access vs adding features).

## Real-world analogy

A **credit card** is a proxy for cash in your account — same “pay” gesture, with limits and authorization behind the scenes.

## Example

### Python

```python
from abc import ABC, abstractmethod


class Image(ABC):
    @abstractmethod
    def display(self) -> None: ...


class RealImage(Image):
    def __init__(self, path: str) -> None:
        self._path = path
        print(f"Loading {path} from disk...")  # expensive

    def display(self) -> None:
        print(f"Showing {self._path}")


class ImageProxy(Image):
    def __init__(self, path: str) -> None:
        self._path = path
        self._real: RealImage | None = None

    def display(self) -> None:
        if self._real is None:
            self._real = RealImage(self._path)  # lazy
        self._real.display()


img: Image = ImageProxy("photo.png")
# not loaded yet
img.display()  # loads once
img.display()  # reuses
```

### Go

```go
type Image interface {
    Display()
}

type RealImage struct{ path string }

func NewRealImage(path string) *RealImage {
    fmt.Println("Loading", path, "from disk...")
    return &RealImage{path: path}
}

func (r *RealImage) Display() { fmt.Println("Showing", r.path) }

type ImageProxy struct {
    path string
    real *RealImage
}

func (p *ImageProxy) Display() {
    if p.real == nil {
        p.real = NewRealImage(p.path)
    }
    p.real.Display()
}
```

## When to use

- Lazy initialization of expensive objects.
- Access control / auditing before delegating.
- Caching results of costly calls.
- Remote proxy: local object representing a remote service.

## When not to use / pitfalls

- If you only add behavior and always forward, you may be writing a **Decorator** — name it honestly.
- Proxies that do too much (cache + auth + retry + metrics) become muddled; split wrappers.
- Caching proxies need invalidation strategy — say so.
- Hidden network/IO in a “simple” proxy surprises callers (latency, failures).

## Interview trigger phrase

> “I’d use a virtual proxy so the heavy image loads only on first display — same Image interface.”

## Exercise

`Document.open()` is allowed only for users with role `editor`.

1. Sketch a protection Proxy around `Document`.
2. What does the proxy do on unauthorized access?
3. One line: Proxy vs Decorator.
