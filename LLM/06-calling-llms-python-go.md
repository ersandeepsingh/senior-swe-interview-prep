# 06 · Calling LLMs via APIs (Python & Go)

**One-line definition:** Calling an LLM is just an HTTPS POST with a JSON body (model + messages + options); you read the JSON response for the generated text and token usage.

---

## Plain English

An LLM API is a normal REST endpoint. You send:

- **which model** you want (`model`),
- **the conversation** as a list of `messages` (each has a `role` and `content`),
- some **knobs** (`max_tokens`, `temperature`, etc.).

You get back JSON containing the model's reply and a `usage` object telling you how many tokens you spent (that's your bill). Everything else — streaming, retries, timeouts — is standard HTTP engineering wrapped around that one call.

The OpenAI **Chat Completions** shape is the de-facto industry standard: most providers (OpenAI, Azure OpenAI, Groq, Together, Fireworks, local servers like vLLM/Ollama) accept the same body. So learn one shape and swap the `base_url` + `model` per provider.

---

## Essentials

### Request body fields

| Field | Type | Meaning | Notes |
|-------|------|---------|-------|
| `model` | string | Which model to run | e.g. `gpt-4o-mini`, `claude-3-5-sonnet` |
| `messages` | array | Conversation history | Each item: `{ "role": ..., "content": ... }` |
| `max_tokens` | int | Cap on **output** length | Guards cost & latency |
| `temperature` | float 0–2 | Randomness | `0` = deterministic-ish, `0.7` = creative |
| `top_p` | float 0–1 | Nucleus sampling | Usually tune temp **or** top_p, not both |
| `stream` | bool | Stream tokens as they generate | Server-Sent Events (SSE) |
| `stop` | string/array | Early-stop sequences | Optional |

### Message roles

| Role | Purpose |
|------|---------|
| `system` | Instructions/persona that steer the whole conversation |
| `user` | The human/app input |
| `assistant` | Previous model replies (for multi-turn context) |
| `tool` | Result returned from a tool/function call |

### Response shape (Chat Completions)

```json
{
  "id": "chatcmpl-123",
  "model": "gpt-4o-mini",
  "choices": [
    {
      "index": 0,
      "message": { "role": "assistant", "content": "Hello!" },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 5,
    "total_tokens": 17
  }
}
```

- Text lives at `choices[0].message.content`.
- Token spend lives at `usage`.
- `finish_reason`: `stop` (done), `length` (hit `max_tokens`), `tool_calls` (wants a tool), `content_filter`.

---

## Examples

### Python — `openai` SDK style (recommended)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],  # never hardcode secrets
    # base_url="https://api.groq.com/openai/v1",  # swap provider here
    timeout=30.0,      # fail fast instead of hanging
    max_retries=2,     # SDK retries transient 429/5xx with backoff
)

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Explain tokens in one sentence."},
    ],
    max_tokens=100,
    temperature=0.2,
)

print(resp.choices[0].message.content)
print("tokens:", resp.usage.total_tokens)
```

### Python — raw `requests` (provider-agnostic REST)

```python
import os, requests

url = "https://api.openai.com/v1/chat/completions"
headers = {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}
payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Ping"}],
    "max_tokens": 50,
    "temperature": 0.2,
}

r = requests.post(url, headers=headers, json=payload, timeout=30)
r.raise_for_status()
data = r.json()
print(data["choices"][0]["message"]["content"])
print("tokens:", data["usage"]["total_tokens"])
```

### Go — `net/http` (provider-agnostic REST)

```go
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

type message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type chatRequest struct {
	Model       string    `json:"model"`
	Messages    []message `json:"messages"`
	MaxTokens   int       `json:"max_tokens"`
	Temperature float64   `json:"temperature"`
}

type chatResponse struct {
	Choices []struct {
		Message      message `json:"message"`
		FinishReason string  `json:"finish_reason"`
	} `json:"choices"`
	Usage struct {
		PromptTokens     int `json:"prompt_tokens"`
		CompletionTokens int `json:"completion_tokens"`
		TotalTokens      int `json:"total_tokens"`
	} `json:"usage"`
}

func main() {
	body, _ := json.Marshal(chatRequest{
		Model:       "gpt-4o-mini",
		Messages:    []message{{Role: "user", Content: "Ping"}},
		MaxTokens:   50,
		Temperature: 0.2,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	req, _ := http.NewRequestWithContext(ctx, http.MethodPost,
		"https://api.openai.com/v1/chat/completions", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+os.Getenv("OPENAI_API_KEY"))

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	var out chatResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		panic(err)
	}
	fmt.Println(out.Choices[0].Message.Content)
	fmt.Println("tokens:", out.Usage.TotalTokens)
}
```

### Streaming basics (why & how)

Streaming sends partial tokens as they're generated using **SSE** (`data: {...}` chunks, ending with `data: [DONE]`). Use it for chat UIs so users see text immediately (lower *perceived* latency). Total tokens/cost are the same.

Python (SDK):

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Count to 5"}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

Go idea: set `"stream": true`, then read `resp.Body` line-by-line with a `bufio.Scanner`, strip the `data: ` prefix, and `json.Unmarshal` each chunk (skip the final `[DONE]`).

### Timeouts & retries (the part interviews probe)

| Concern | Python | Go |
|---------|--------|-----|
| Timeout | `timeout=30` on client/request | `context.WithTimeout` |
| Retries | SDK `max_retries`; else loop with backoff | manual loop with backoff |
| What to retry | `429`, `500`, `502`, `503`, timeouts | same |
| What NOT to retry | `400` (bad request), `401` (auth) | same |

Retry pattern: exponential backoff **with jitter**, respect the `Retry-After` header, cap attempts (2–4).

---

## When to use / trade-offs

| Choice | Use when | Trade-off |
|--------|----------|-----------|
| Provider SDK | Fast dev, built-in retries | One more dependency, per-provider |
| Raw HTTP | Full control, provider-agnostic, thin services | You own retries/streaming parsing |
| Streaming | Interactive chat UIs | Harder error handling; can't retry mid-stream |
| Non-streaming | Batch / server-to-server | Higher perceived latency |

---

## Pitfalls

- **No timeout** → a hung request stalls a worker/goroutine forever. Always set one.
- **Retrying non-idempotent 4xx** → wastes money and spams the API. Only retry `429`/`5xx`/timeouts.
- **Ignoring `finish_reason: length`** → your answer got truncated by `max_tokens`; you silently ship half a response.
- **Hardcoding keys** → leak risk. Always read from env / secrets manager.
- **Assuming one shape fits all** → some providers differ on tool-calling and streaming details; test per provider.
- **Not reading `usage`** → you fly blind on cost.

---

## Interview trigger phrase

> "Calling an LLM is a JSON POST with `model` + `messages` + knobs; I read `choices[].message.content` and the `usage` object, wrap it with a timeout and bounded backoff retries on 429/5xx, and stream via SSE only for interactive UIs."

---

## Exercise

Write a small function (Python **or** Go) `ask(prompt) -> (text, total_tokens)` that:

1. Reads the API key from an env var (fail clearly if missing).
2. POSTs a single user message with `max_tokens=150`, `temperature=0`.
3. Enforces a 20s timeout.
4. Retries up to 3 times on `429`/`5xx` with exponential backoff + jitter, but never on `400`/`401`.
5. Returns the text and `usage.total_tokens`, and logs a warning if `finish_reason == "length"`.
