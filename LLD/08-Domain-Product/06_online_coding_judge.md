# Online Coding Judge

> Submissions, verdicts, sandboxing — **Command** (run job) + **State** + **Observer**. 🔴

## Scope / requirements

**In:** submit code against a problem, queue execution, produce verdict (`QUEUED → RUNNING → ACCEPTED/WA/TLE/RE/CE`), store results, notify user.

**Out:** real secure sandbox (Docker/gVisor) implementation — model as `Executor` port; multi-language compilers as strategies.

## Entities

| Entity | Owns |
|--------|------|
| `Problem`, `TestCase` | statement meta, hidden/visible cases |
| `Submission` | code, language, status, verdict |
| `JudgeJob` / Command | encapsulate “run this submission” |
| `Executor` | sandbox run interface |
| `VerdictObserver` | websocket / email |

## Invariants

- Submission status only moves forward via judge pipeline.
- Verdict is derived from all test cases (fail-fast or full run — declare).
- Executor timeouts must mark `TLE`, not hang the worker forever.
- Same submission id processed once (idempotent judge).

## Interfaces / patterns — and why

| Seam | Pattern | Why |
|------|---------|-----|
| Run request | **Command** | Queueable, retryable unit of work |
| Submission lifecycle | **State** | UI and retries depend on status |
| Language / runner | **Strategy** / Factory | `python` vs `go` compile+run |
| Completion | **Observer** | Push verdict without coupling API to WS |

## End-to-end flow

1. User submits → `Submission(QUEUED)` → enqueue `JudgeCommand`.
2. Worker dequeues → `RUNNING` → `Executor.run` per test case.
3. Aggregate verdict → terminal state → notify observers.

## Skeletons

### Python

```python
from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass


class Status(Enum):
    QUEUED = auto()
    RUNNING = auto()
    ACCEPTED = auto()
    WA = auto()
    TLE = auto()
    RE = auto()
    CE = auto()


@dataclass
class TestCase:
    input: str
    expected: str
    time_limit_ms: int


class Executor(ABC):
    @abstractmethod
    def run(self, code: str, language: str, tc: TestCase) -> tuple[str, Status]:
        """returns (stdout_or_err, case_status)"""
        ...


class Submission:
    def __init__(self, id: str, code: str, language: str):
        self.id, self.code, self.language = id, code, language
        self.status = Status.QUEUED
        self.verdict: Status | None = None


class JudgeService:
    def __init__(self, executor: Executor, observers: list):
        self._exec, self._observers = executor, observers

    def judge(self, sub: Submission, cases: list[TestCase]) -> None:
        sub.status = Status.RUNNING
        for tc in cases:
            _, case_status = self._exec.run(sub.code, sub.language, tc)
            if case_status != Status.ACCEPTED:
                sub.status = case_status
                sub.verdict = case_status
                self._notify(sub)
                return
        sub.status = Status.ACCEPTED
        sub.verdict = Status.ACCEPTED
        self._notify(sub)

    def _notify(self, sub: Submission) -> None:
        for o in self._observers:
            o.on_verdict(sub.id, sub.verdict)
```

### Go

```go
type Executor interface {
    Run(code, language string, tc TestCase) (stdout string, status Status)
}

type JudgeService struct {
    Exec      Executor
    Observers []VerdictObserver
}

func (j *JudgeService) Judge(sub *Submission, cases []TestCase) {
    sub.Status = Running
    for _, tc := range cases {
        _, st := j.Exec.Run(sub.Code, sub.Language, tc)
        if st != Accepted {
            sub.Status, sub.Verdict = st, st
            j.notify(sub)
            return
        }
    }
    sub.Status, sub.Verdict = Accepted, Accepted
    j.notify(sub)
}
```

## Concurrency / consistency

- Worker pool = **Producer–Consumer** on submission queue; bound queue to protect executors.
- One submission → one in-flight judge (dedupe by submission id).
- Isolate timeouts with context deadlines; never share writable FS between runs (say so).

## Tradeoffs / pitfalls

- Running untrusted code in-process — always behind `Executor` port.
- Storing only final verdict without per-case detail when debugging WA.
- Blocking API thread on judge — queue async.

## Interview prompts

- Where does Command help vs plain function call?
- Fail-fast vs run-all test cases?
- How do you scale judges horizontally?

## Exercise / follow-ups

1. Add `LanguageRunner` Factory mapping `python`/`go` to executors.
2. Model compile step → `CE` before tests.
3. Sketch retry policy for infra failures (not for WA).
