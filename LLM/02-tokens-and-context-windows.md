# Tokens and Context Windows

> **One-line definition:** A **token** is the unit of text an LLM reads and writes (roughly a word-piece), and the **context window** is the maximum number of tokens the model can consider in a single request.

---

## Plain English

LLMs don't see letters or words — they see **tokens**. A token is a common chunk of text: sometimes a whole word (`" dog"`), sometimes a piece (`"un" + "believ" + "able"`), sometimes punctuation or a space.

Everything is measured and billed in tokens: what you send (**input**) and what you get back (**output**). The **context window** is the total token budget for one call — input + output must fit inside it. Go over, and you must truncate, summarize, or split.

---

## Essentials

### Key terms

| Term | Meaning |
|------|---------|
| **Token** | Smallest text unit the model processes (~a word-piece) |
| **Tokenization** | Splitting raw text into tokens before the model sees it |
| **Input tokens** | Everything you send: system prompt + history + user message + tool schemas |
| **Output tokens** | Everything the model generates in its reply |
| **Context window** | Max total tokens (input + output) for one request |
| **Truncation** | Cutting text to fit the window |

### The ~4 chars/token rule

A handy estimate for English:

```text
1 token  ≈ 4 characters  ≈ ¾ of a word
1,000 tokens ≈ ~750 words ≈ ~1.5 pages of text
```

So "1000 tokens" is **not** 1000 words. Code, JSON, and non-English text tokenize less efficiently (more tokens per character).

### Input vs output

Both count, but they differ in two ways:

| | Input tokens | Output tokens |
|--|--------------|---------------|
| Contains | Prompt, history, docs, tool defs | The model's generated reply |
| Usually priced | Cheaper per token | More expensive per token |
| You control by | Trimming context, RAG | `max_tokens`, asking for brevity |

### What counts toward the window

Everything you pass in each call: **system prompt + full message history + retrieved documents + tool/function schemas + the user's new message + the space reserved for the answer.** History is the sneaky one — long chats grow every call.

### Example window sizes (illustrative)

| Window size | Roughly holds | Typical use |
|-------------|---------------|-------------|
| 8K tokens | ~6K words | Short chats, simple tasks |
| 128K tokens | ~96K words / ~200 pages | Long docs, big codebases |
| 1M tokens | ~750K words | Whole repos, many documents |

---

## Simple example

```python
# Estimate before you send (rough client-side check)
text = open("contract.txt").read()
approx_tokens = len(text) / 4          # ~4 chars per token
if approx_tokens > 100_000:
    text = summarize_or_chunk(text)    # don't blow the window

# Many SDKs return exact usage after the call:
# resp.usage -> {prompt_tokens, completion_tokens, total_tokens}
```

---

## What overflows and how to handle it

| Problem | Symptom | Fix |
|---------|---------|-----|
| Prompt too long | API error / rejected request | Truncate, summarize, or chunk input |
| History keeps growing | Rising cost & latency each turn | Keep a rolling window; summarize old turns |
| Huge document | Won't fit even in big window | **RAG**: retrieve only relevant chunks |
| Answer gets cut off | Reply ends mid-sentence | Raise `max_tokens`; leave room in the window |

**Rule of thumb:** reserve output space. If the window is 8K and you need a 1K-token answer, keep input under ~7K.

---

## When to use / trade-offs

- **Bigger window** = simpler code (dump everything in) but higher cost and latency, and models can "lose" details in the middle of very long contexts.
- **Smaller window + RAG/summarization** = cheaper and faster, but more engineering and a chance of retrieving the wrong chunk.
- Don't pay for a 1M-token window if 8K solves your task.

---

## Pitfalls

- **Confusing tokens with words** when estimating cost (see file on cost/pricing).
- **Forgetting history counts.** Long conversations silently balloon input tokens every turn.
- **Ignoring tool schemas.** Function definitions live in the input and eat tokens too.
- **No output budget.** Not reserving room for the answer → truncated replies.
- **Assuming code tokenizes like prose.** It usually costs more tokens per character.

---

## Interview trigger phrase

> "Tokens are the billing and context unit — input + output must fit the context window. I estimate with ~4 chars/token, reserve room for the output, and use rolling summaries or RAG so history and documents don't overflow the window."

---

## Exercise

You have a 40-page PDF (~20,000 words) and an 8K-token model.
1. Estimate the tokens for the PDF. Does it fit?
2. Name two strategies to get an answer without upgrading the model.
3. If a chat has been going for 30 turns and responses are getting slow and pricey, what's the likely cause and one fix?
