# Facade

> Provide a **simple, unified interface** to a complex subsystem of classes.

## Plain English

Clients shouldn’t need to know about demuxers, codecs, and filters to convert a video. A `VideoConverter.convert(file, format)` facade orchestrates the messy bits behind one call.

## Why seniors get asked this

Seniors shrink cognitive load: expose a clean application API over libraries/domain subsystems. Interviewers like hearing “I’ll hide this complexity behind a facade” without pretending complexity vanished.

## Real-world analogy

A **hotel concierge**: you ask for dinner reservations; they coordinate restaurant, taxi, and timing — you don’t call each vendor.

## Example

### Python

```python
class AudioMixer:
    def mix(self, tracks: list[str]) -> str:
        return f"mixed({'+'.join(tracks)})"


class VideoDecoder:
    def decode(self, path: str) -> str:
        return f"frames:{path}"


class Encoder:
    def encode(self, frames: str, fmt: str) -> str:
        return f"{frames}->{fmt}"


class VideoConverter:  # Facade
    def __init__(self) -> None:
        self._decoder = VideoDecoder()
        self._mixer = AudioMixer()
        self._encoder = Encoder()

    def convert(self, path: str, fmt: str) -> str:
        frames = self._decoder.decode(path)
        _ = self._mixer.mix(["a1", "a2"])
        return self._encoder.encode(frames, fmt)


print(VideoConverter().convert("movie.mp4", "mp4"))
```

### Go

```go
type AudioMixer struct{}
func (AudioMixer) Mix(tracks []string) string {
    return "mixed(" + strings.Join(tracks, "+") + ")"
}

type VideoDecoder struct{}
func (VideoDecoder) Decode(path string) string { return "frames:" + path }

type Encoder struct{}
func (Encoder) Encode(frames, fmt string) string {
    return frames + "->" + fmt
}

type VideoConverter struct { // Facade
    decoder VideoDecoder
    mixer   AudioMixer
    encoder Encoder
}

func (v VideoConverter) Convert(path, fmt string) string {
    frames := v.decoder.Decode(path)
    _ = v.mixer.Mix([]string{"a1", "a2"})
    return v.encoder.Encode(frames, fmt)
}
```

## When to use

- Subsystem has many moving parts; most callers need one or two workflows.
- You want a stable API while internals churn.
- Layering: application service as facade over domain services.

## When not to use / pitfalls

- Don’t force *all* access through the facade if advanced callers need internals — optional escape hatches are ok.
- A “God facade” that does everything becomes a God class (SRP).
- Not the same as **Adapter** (one foreign interface) — Facade simplifies *many* collaborators.
- Facades can hide too much and make debugging harder; keep orchestration obvious.

## Interview trigger phrase

> “I’d expose a thin VideoConverter facade so callers don’t wire codecs and filters themselves.”

## Exercise

Checkout needs inventory reserve, payment charge, and email — three services.

1. Sketch a `CheckoutFacade.placeOrder(...)` that orchestrates them.
2. Should the facade own business rules or only sequence calls?
3. How does this differ from Adapter?
