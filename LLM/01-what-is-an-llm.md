# What an LLM Is and How It Works

> **One-line definition:** A Large Language Model (LLM) is a neural network that, given some text, predicts the next chunk of text one token at a time — and by doing that well, it can answer questions, write code, and follow instructions.

---

## Plain English

An LLM is fundamentally a **very good autocomplete**. You give it text, and it guesses what should come next. That's it.

The "magic" is that to guess the next word well across the entire internet's worth of text, the model has to internalize grammar, facts, reasoning patterns, code syntax, and more. Being good at prediction *forces* it to learn something that looks like understanding.

It does **not** think, plan ahead, or "know" things the way a database does. It has no live internet access, no memory between calls (unless you send it), and no built-in sense of truth. It produces the most statistically plausible continuation of your text.

---

## Essentials

### Next-token prediction

The model reads your text, converts it to tokens (word pieces), and outputs a probability distribution over *all possible next tokens*. It picks one, appends it, and repeats until it decides to stop.

```text
Input:  "The capital of France is"
Model:  P("Paris")=0.92, P("Lyon")=0.03, P("a")=0.02, ...
Output: "Paris"   → then predicts the next token, and so on
```

### Training vs inference

| Phase | What happens | When | Cost you pay |
|-------|--------------|------|--------------|
| **Training** | Model learns weights from huge text corpora (done by the model provider) | Once, before release | Nothing (baked in) |
| **Inference** | You send a prompt, model predicts tokens using frozen weights | Every API call | Per-token cost + latency |

You almost never train. You **do** inference on every request. Optimizing your app = optimizing inference (prompt size, model choice, caching).

### Transformer intuition (no heavy math)

The architecture behind modern LLMs is the **transformer**. The key idea is **attention**: when predicting the next token, the model looks back at all previous tokens and decides *which ones matter most* right now.

Analogy: reading the sentence "The trophy didn't fit in the suitcase because **it** was too big." To resolve "it," you pay attention to "trophy," not "suitcase." Attention lets the model weigh relevant words regardless of distance.

That's the whole intuition — you don't need the matrix math to reason about behavior.

### What it can and can't do

| Can do well | Struggles / can't do |
|-------------|----------------------|
| Summarize, rewrite, translate | Reliable exact arithmetic on long numbers |
| Draft & explain code | Know events after its knowledge cutoff |
| Follow instructions, format output | Access live data (no internet unless given tools) |
| Extract structured data from text | Guarantee factual correctness |
| Classify, route, tag | Remember past chats (stateless unless you resend) |

### Model families: base vs instruct/chat

| Type | Trained for | Behavior | Use for |
|------|-------------|----------|---------|
| **Base** | Raw next-token prediction | Just continues text; won't "obey" | Research, fine-tuning starting point |
| **Instruct / Chat** | Base + instruction tuning + alignment (RLHF) | Follows commands, answers questions, uses chat roles | Almost all app integrations |

For building app APIs, you want an **instruct/chat** model. Base models will happily continue your prompt instead of answering it.

---

## Simple example

```python
# Pseudocode: one inference call to a chat model
resp = client.chat.completions.create(
    model="gpt-4o-mini",          # an instruct/chat model
    messages=[{"role": "user", "content": "Explain a mutex in one sentence."}],
)
print(resp.choices[0].message.content)
# Under the hood: model predicted tokens one by one until it emitted a stop token.
```

---

## When to use / trade-offs

- **Use an LLM** when the task is fuzzy, language-heavy, or needs flexible reasoning (summarization, extraction, drafting, classification of messy text).
- **Don't use an LLM** when a deterministic rule, regex, SQL query, or plain function is cheaper and exact. LLMs are probabilistic; don't use them for things that must be 100% correct and are easily coded.

---

## Pitfalls

- **Treating it as a knowledge base.** It's a prediction engine, not a source of truth. Ground it with your own data when facts matter.
- **Assuming memory.** Each API call is stateless. If you don't resend context, it "forgets."
- **Using a base model in an app.** It won't follow instructions — pick instruct/chat.
- **Expecting determinism.** Same prompt can give different outputs (see file 04).

---

## Interview trigger phrase

> "An LLM is a next-token predictor built on transformer attention; at inference it's a stateless function from tokens to tokens — so I design my system to *supply* it with the right context and *never* rely on it as the source of truth."

---

## Exercise

Take the sentence: *"I need to summarize 200 customer reviews and flag angry ones."*
1. Which part is a good LLM job and which could be plain code?
2. Would you pick a base or instruct model, and why?
3. In one line, explain what "stateless inference" means for how you'd send the 200 reviews.
