# Logging Framework

> Levels, appenders, formatters → **Chain of Responsibility + Strategy**. 🟡

## Scope / Requirements

**In scope**
- Log levels: DEBUG < INFO < WARN < ERROR.
- Logger API: `debug/info/warn/error(msg)`.
- Multiple appenders (console, file); pluggable formatters.
- Level filter: message only emitted if ≥ configured level.

**Out of scope**
- Distributed tracing backends, log shipping agents, full async disruptor.

**Domain invariants**
- A log event has level, message, timestamp (and optional context).
- Filtering: if event.level < logger.level → no appenders called.
- Chain: each handler may write and/or pass to next (or use fan-out list — both OK; CoR is classic interview framing).
- Formatters are pure: event → string; appenders only I/O.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `LogLevel` | Ordered severity. |
| `LogEvent` | Payload. |
| `Formatter` | Strategy: render string. |
| `Appender` | Destination write. |
| `Logger` | Filter by level; dispatch. |
| `Handler` (CoR) | Optional wrap: level gate + appender + next. |

## Key Interfaces / Patterns

- **Chain of Responsibility:** handler chain with level thresholds (like log4j).
- **Strategy — Formatter / Appender.**
- **Singleton (careful):** root logger — mention thread-safe init, don’t over-rotate.

## End-to-End Flow

1. `logger.info("started")` builds `LogEvent`.
2. Level check passes → format → each appender writes.
3. `debug` discarded if logger level is INFO.

## Python Skeleton

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


class Level(IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40


@dataclass
class LogEvent:
    level: Level
    message: str
    ts: datetime


class Formatter(ABC):
    @abstractmethod
    def format(self, e: LogEvent) -> str: ...


class SimpleFormatter(Formatter):
    def format(self, e: LogEvent) -> str:
        return f"{e.ts.isoformat()} {e.level.name} {e.message}"


class Appender(ABC):
    @abstractmethod
    def append(self, line: str) -> None: ...


class ConsoleAppender(Appender):
    def append(self, line: str) -> None:
        print(line)


class FileAppender(Appender):
    def __init__(self, path: str):
        self.path = path

    def append(self, line: str) -> None:
        with open(self.path, "a") as f:
            f.write(line + "\n")


class Handler(ABC):
    def __init__(self, level: Level, next: Handler | None = None):
        self.level = level
        self.next = next

    def handle(self, e: LogEvent) -> None:
        if e.level >= self.level:
            self.write(e)
        if self.next:
            self.next.handle(e)

    @abstractmethod
    def write(self, e: LogEvent) -> None: ...


class AppenderHandler(Handler):
    def __init__(self, level: Level, appender: Appender, formatter: Formatter, next: Handler | None = None):
        super().__init__(level, next)
        self.appender = appender
        self.formatter = formatter

    def write(self, e: LogEvent) -> None:
        self.appender.append(self.formatter.format(e))


class Logger:
    def __init__(self, level: Level, handler: Handler):
        self.level = level
        self.handler = handler

    def _log(self, level: Level, msg: str) -> None:
        if level < self.level:
            return
        self.handler.handle(LogEvent(level, msg, datetime.utcnow()))

    def debug(self, msg: str) -> None: self._log(Level.DEBUG, msg)
    def info(self, msg: str) -> None: self._log(Level.INFO, msg)
    def warn(self, msg: str) -> None: self._log(Level.WARN, msg)
    def error(self, msg: str) -> None: self._log(Level.ERROR, msg)
```

## Go Skeleton

```go
package logging

import (
    "fmt"
    "os"
    "time"
)

type Level int

const (
    DEBUG Level = 10
    INFO  Level = 20
    WARN  Level = 30
    ERROR Level = 40
)

type Event struct {
    Level Level
    Msg   string
    TS    time.Time
}

type Formatter interface{ Format(Event) string }
type Appender interface{ Append(string) }

type SimpleFormatter struct{}

func (SimpleFormatter) Format(e Event) string {
    return fmt.Sprintf("%s %d %s", e.TS.Format(time.RFC3339), e.Level, e.Msg)
}

type ConsoleAppender struct{}

func (ConsoleAppender) Append(line string) { fmt.Println(line) }

type Handler struct {
    Level     Level
    Appender  Appender
    Formatter Formatter
    Next      *Handler
}

func (h *Handler) Handle(e Event) {
    if e.Level >= h.Level {
        h.Appender.Append(h.Formatter.Format(e))
    }
    if h.Next != nil {
        h.Next.Handle(e)
    }
}

type Logger struct {
    Level   Level
    Handler *Handler
}

func (l *Logger) log(level Level, msg string) {
    if level < l.Level {
        return
    }
    l.Handler.Handle(Event{Level: level, Msg: msg, TS: time.Now()})
}

func (l *Logger) Info(msg string)  { l.log(INFO, msg) }
func (l *Logger) Error(msg string) { l.log(ERROR, msg) }

// FileAppender sketch
type FileAppender struct{ Path string }

func (f FileAppender) Append(line string) {
    file, _ := os.OpenFile(f.Path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    defer file.Close()
    _, _ = file.WriteString(line + "\n")
}
```

## Concurrency / Consistency

- Appenders may block; async queue + worker is a common extension.
- Shared `FileAppender` needs a mutex or channel serialization.
- Never let logging throw into business flow — swallow/append errors carefully.

## Extensions / Trade-offs / Pitfalls

- Async logging + batching; MDC/context fields.
- Pitfall: string formatting before level check (wasted work) — lazy messages.
- Fan-out list vs CoR — CoR shines with per-handler min level (ERROR→pager, INFO→file).

## Interview Discussion Points

- Why CoR vs `for appender in appenders`?
- How would you add JSON formatting without touching Logger?
- Performance: allocations, async handoff.

## Exercise

Wire Logger(INFO) → console handler + file handler that only accepts ERROR+.

**Follow-ups**
1. Add `JsonFormatter` via Strategy only.
2. Make file appends thread-safe.
3. Design async logging with a bounded queue and drop policy.
