# Python Interview Topic Map — Basic → Advanced

Organized by **category → topic → 1-line "what to know."**
Ordered roughly basic → advanced. The ⭐ marks topics interviewers probe hardest (especially for senior roles) — data-model/dunders, generators, concurrency/GIL, memory, and the classic gotchas.

Legend: 🟢 basic · 🟡 intermediate · 🔴 advanced/senior-signal · ⭐ high-frequency

---

## 1. Language Fundamentals

- **Dynamic typing & names-as-references** — variables are labels bound to objects, not boxes. 🟢⭐
- **Everything is an object** — functions, classes, modules are all first-class objects. 🟢⭐
- **Numeric types** — int (arbitrary precision), float, complex, bool as int subclass. 🟢
- **Truthiness** — falsy values (`0`, `""`, `[]`, `{}`, `None`), `bool()` protocol. 🟢⭐
- **`is` vs `==`** — identity vs equality; small-int/string interning gotcha. 🟡⭐
- **`None`, `pass`, `...` (Ellipsis)** — sentinels and placeholders. 🟢
- **String basics** — immutability, f-strings, formatting, common methods. 🟢
- **Control flow** — `for`/`else`, `while`/`else`, `match` (3.10+ structural pattern matching). 🟡
- **Comprehensions** — list/dict/set comprehensions, nested, conditional. 🟢⭐
- **Walrus operator `:=`** — assignment expressions (3.8+). 🟡

## 2. Built-in Data Structures ⭐

- **Lists** — dynamic array, slicing, mutation, O() of common ops. 🟢⭐
- **Tuples** — immutable, hashable (if elements are), packing/unpacking. 🟢
- **Dicts** — hash map, insertion order (3.7+), `get`/`setdefault`, dict views. 🟢⭐
- **Sets & frozensets** — membership, set algebra, hashing requirement. 🟢
- **Slicing deep** — `[start:stop:step]`, negative indices, slice assignment. 🟡⭐
- **Mutable vs immutable** — which types are which and why it matters. 🟡⭐
- **Unpacking** — `*args`/`**kwargs`, starred assignment, dict merge `{**a, **b}` / `|`. 🟡⭐
- **`collections`** — `defaultdict`, `Counter`, `deque`, `OrderedDict`, `namedtuple`. 🟡⭐
- **`heapq` / `bisect`** — priority queue & sorted insertion. 🟡
- **`array` / `bytes` / `bytearray`** — compact/binary sequences. 🟡

## 3. Functions

- **Arguments** — positional, keyword, defaults, keyword-only, positional-only (`/`). 🟢⭐
- **`*args` / `**kwargs`** — variadic capture and forwarding. 🟢⭐
- **Mutable default argument trap** — `def f(x=[])` shared across calls. 🔴⭐
- **First-class & higher-order functions** — pass/return functions, `map`/`filter`/`sorted` keys. 🟢
- **Lambdas** — anonymous functions and their limits. 🟢
- **Closures** — capturing enclosing scope, `nonlocal`, late-binding loop gotcha. 🔴⭐
- **Scope & LEGB rule** — Local/Enclosing/Global/Built-in, `global`/`nonlocal`. 🟡⭐
- **Recursion** — recursion limit, why Python has no TCO. 🟡

## 4. OOP & the Data Model ⭐

- **Classes & instances** — `__init__`, instance vs class attributes. 🟢⭐
- **`self` and methods** — bound vs unbound, `@classmethod`, `@staticmethod`. 🟡⭐
- **Inheritance & `super()`** — single & multiple inheritance. 🟡⭐
- **MRO (C3 linearization)** — how method resolution order works in diamond inheritance. 🔴⭐
- **Dunder / magic methods** — `__str__`/`__repr__`, `__eq__`/`__hash__`, `__len__`, `__getitem__`, `__call__`, `__enter__/__exit__`. 🔴⭐
- **Operator overloading** — `__add__`, `__lt__`, rich comparisons. 🟡
- **`@property`** — getters/setters, computed attributes. 🟡⭐
- **Descriptors** — `__get__`/`__set__`, how `property`/methods work underneath. 🔴⭐
- **`__slots__`** — memory savings & attribute restriction. 🔴⭐
- **`dataclasses`** — auto `__init__`/`__repr__`/`__eq__`, `field`, frozen. 🟡⭐
- **`Enum`, `NamedTuple`, `TypedDict`** — structured value types. 🟡
- **Abstract base classes** — `abc`, `@abstractmethod`, duck typing vs ABCs. 🟡
- **`__new__` vs `__init__`** — object creation vs initialization (singletons, immutables). 🔴

## 5. Iterators, Generators & Comprehensions ⭐

- **Iterator protocol** — `__iter__`/`__next__`, `StopIteration`. 🟡⭐
- **Iterable vs iterator** — the distinction and why it matters. 🟡⭐
- **Generators** — `yield`, lazy evaluation, memory efficiency. 🔴⭐
- **Generator expressions** — `(x for x in ...)` vs list comp. 🟡
- **`yield from`** — delegating to sub-generators. 🔴
- **Coroutines via generators** — `send`/`throw`/`close` (pre-async history). 🔴
- **`itertools`** — `chain`, `groupby`, `product`, `islice`, `cycle`, `accumulate`. 🟡⭐

## 6. Decorators & Metaprogramming 🔴

- **Decorators** — wrapping functions, `functools.wraps`. 🔴⭐
- **Decorators with arguments** — decorator factories (3 levels of nesting). 🔴⭐
- **Class decorators** — modifying/registering classes. 🔴
- **`functools`** — `lru_cache`/`cache`, `partial`, `reduce`, `singledispatch`. 🟡⭐
- **Context managers** — `with`, `__enter__`/`__exit__`, `contextlib.contextmanager`. 🟡⭐
- **Metaclasses** — `type` as metaclass, `__init_subclass__`, when you'd actually use one. 🔴⭐
- **Monkey patching** — runtime modification, risks. 🔴
- **`getattr`/`setattr`/`__getattr__`/`__getattribute__`** — dynamic attribute access. 🔴

## 7. Error Handling

- **`try`/`except`/`else`/`finally`** — full flow and when `else` runs. 🟢⭐
- **Exception hierarchy** — `BaseException` vs `Exception`, catching order. 🟡⭐
- **Custom exceptions** — subclassing, adding context. 🟡
- **Raising & chaining** — `raise from`, exception context. 🟡
- **`with` for cleanup** — resource management vs try/finally. 🟡
- **EAFP vs LBYL** — "easier to ask forgiveness" idiom. 🟡⭐
- **Exception groups & `except*`** — (3.11+) for concurrent errors. 🔴

## 8. Concurrency & Parallelism ⭐ (senior make-or-break)

- **The GIL** — what it is, why it exists, what it blocks (CPU-bound threads). 🔴⭐
- **Threading** — `threading`, when threads help (I/O-bound), locks/`RLock`/`Event`. 🔴⭐
- **Multiprocessing** — `multiprocessing`, true parallelism, IPC, pickling costs. 🔴⭐
- **`concurrent.futures`** — `ThreadPoolExecutor`/`ProcessPoolExecutor`, `Future`. 🟡⭐
- **asyncio fundamentals** — `async`/`await`, event loop, coroutines. 🔴⭐
- **asyncio primitives** — `gather`, `create_task`, `Queue`, `Lock`, `wait_for`/timeouts. 🔴⭐
- **Blocking in async** — why a blocking call stalls the loop; `run_in_executor`. 🔴⭐
- **Choosing a model** — threads vs processes vs async by workload (I/O vs CPU). 🔴⭐
- **Race conditions & synchronization** — locks, deadlocks, thread-safety. 🔴
- **`queue.Queue`** — thread-safe producer/consumer. 🟡

## 9. Memory Management & Internals 🔴

- **Reference counting** — the primary GC mechanism. 🔴⭐
- **Cyclic garbage collector** — generational GC for reference cycles. 🔴⭐
- **`id()` & object identity** — CPython object model. 🟡
- **Interning** — small ints & some strings cached. 🟡⭐
- **Mutable default & shared-reference bugs** — aliasing pitfalls. 🔴⭐
- **`copy` module** — shallow vs deep copy, `__copy__`/`__deepcopy__`. 🟡⭐
- **`weakref`** — weak references to avoid cycles/caches. 🔴
- **`__slots__` memory impact** — dict-free instances. 🔴
- **`sys.getsizeof` / memory profiling** — measuring footprint. 🔴
- **CPython vs PyPy / interpreters** — GIL-free efforts, JIT trade-offs. 🔴

## 10. Type Hints & Modern Python

- **Type annotations** — `->`, variable annotations, `typing` module. 🟡⭐
- **Common types** — `Optional`, `Union`/`|`, `List`/`list`, `Dict`, `Callable`, `Any`. 🟡⭐
- **Generics & `TypeVar`** — parametric types, `Protocol` (structural typing). 🔴
- **`mypy` / static checking** — gradual typing, when hints are enforced. 🟡
- **`Protocol`** — duck-typing with static checks. 🔴
- **Pydantic / validation (ecosystem)** — runtime type validation. 🟡

## 11. Standard Library Fluency

- **`os` / `sys` / `pathlib`** — filesystem, paths, args, env. 🟢
- **`json` / `csv` / `pickle`** — serialization (and pickle security caveat). 🟡⭐
- **`datetime` / `time`** — timezones, parsing, `timedelta`. 🟡
- **`re`** — regex, groups, `compile`, greedy vs lazy. 🟡⭐
- **`logging`** — levels, handlers, formatters vs `print`. 🟡⭐
- **`argparse`** — CLI parsing. 🟢
- **`unittest` / `pytest`** — test structure, fixtures, mocking (`unittest.mock`). 🟡⭐
- **`dataclasses` / `enum` / `typing`** — modern building blocks. 🟡
- **`asyncio` / `subprocess`** — async & running external processes. 🔴

## 12. Idioms, Best Practices & Performance

- **Pythonic idioms** — unpacking, comprehensions, `enumerate`, `zip`, context managers. 🟡⭐
- **PEP 8 & readability** — style, naming, "one obvious way." 🟢
- **Generators for memory** — streaming vs materializing large data. 🔴⭐
- **`lru_cache` / memoization** — caching expensive calls. 🟡⭐
- **String building** — `join` vs `+=` in loops. 🟡
- **Profiling** — `cProfile`, `timeit`, finding hot spots. 🔴
- **Vectorization (NumPy/pandas)** — avoid Python loops for numeric work. 🔴
- **Packaging & envs** — `venv`, `pip`, `pyproject.toml`, dependency management. 🟡
- **Import system** — modules vs packages, `__init__.py`, circular imports, `if __name__ == "__main__"`. 🟡⭐

## 13. Classic Interview Gotchas (memorize these) ⭐

- **Mutable default arguments** — `def f(x=[])` persists between calls. 🔴⭐
- **Late binding closures in loops** — all lambdas capture the final loop value. 🔴⭐
- **`is` vs `==` with small ints/strings** — interning makes `is` misleadingly work. 🟡⭐
- **Modifying a list while iterating** — skipped elements / surprising behavior. 🟡⭐
- **Shallow vs deep copy** — nested mutation through shared references. 🟡⭐
- **Integer/`bool` identity** — `True == 1`, `isinstance(True, int)`. 🟡
- **Dict/set ordering & hashability** — unhashable keys, insertion order. 🟡
- **`==` vs `__eq__`/`__hash__` contract** — breaking it corrupts dict/set behavior. 🔴⭐
- **Class vs instance attribute shadowing** — mutable class attribute shared across instances. 🔴⭐
- **`+=` on tuples/immutables inside containers** — partial mutation + TypeError. 🔴
- **Chained comparisons** — `a < b < c` semantics. 🟢

---

## Study priority (senior SWE)

1. **Non-negotiable, expect deep questions:** the data model & dunders (`__eq__`/`__hash__`, `__repr__`, context managers, descriptors), generators/iterators, decorators, mutable-default & closure gotchas, GIL + concurrency model choice.
2. **Strong differentiators:** memory management (refcounting + cyclic GC), `__slots__`/`weakref`, metaclasses & `__init_subclass__`, asyncio internals (event loop, blocking pitfalls), type hints & `Protocol`.
3. **Round out:** stdlib fluency (`collections`, `itertools`, `functools`, `re`, `logging`), testing with pytest/mock, packaging & imports, profiling.

How senior Python interviews usually go: a **coding task** (clean, Pythonic, often with generators/comprehensions), a **language-internals grill** ("explain the GIL," "how does `hash`/`eq` work," "shallow vs deep copy," "what's a decorator doing"), and a **debug/gotcha** segment (mutable defaults, closures, identity vs equality). Be ready to write idiomatic code *and* explain what CPython does underneath.
