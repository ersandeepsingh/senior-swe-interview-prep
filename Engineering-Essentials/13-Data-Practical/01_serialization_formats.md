# Serialization Formats

> How you turn in-memory structures into bytes for APIs, queues, and storage. Pick for **speed, size, schema evolution, and ecosystem** — not fashion.

## Plain English

Encoding choice is a trade of human-friendliness vs size/speed vs schema discipline. **Schema evolution** rules matter more than the binary format itself.

```text
  Producer v2 adds optional email
  Consumer v1 ignores unknown field → OK (forward compatible writer / backward compatible reader)
```

## Essentials (must-know for this topic)

### Format trade-offs

| Format | Shape | Schema | Sweet spot |
|--------|-------|--------|------------|
| **JSON** | Text, human-readable | Informal / JSON Schema | Public APIs, config, debugging |
| **Protobuf** | Compact binary | Required `.proto` IDL | gRPC, internal RPC |
| **Avro** | Compact binary | Schema (often + registry) | Kafka / data pipelines |
| **MessagePack** | Compact binary | Optional | JSON-like speedup without full IDL culture |
| **Parquet / ORC** | Columnar on disk | Schema | Analytics / warehouse scans |

### JSON vs Protobuf vs Avro

| | JSON | Protobuf | Avro |
|---|------|----------|------|
| Readable | Yes | No (needs tooling) | No |
| Size / parse cost | Larger / costlier | Compact / fast | Compact |
| Contract | Weak unless JSON Schema | Strict `.proto` | Schema + registry culture |
| Evolution | Easy to drift silently | Field numbers + rules | Compatibility checks at produce time |
| Typical home | External HTTP APIs | Service-to-service RPC | Event buses / lakes |

### Evolution rules (belong with serialization)

| Usually OK | Breaking |
|------------|----------|
| Add optional field with default | Remove / rename required field |
| Readers ignore unknown fields | Change type / meaning in place |
| Optional → still optional | Suddenly require a new field on old producers |

## Simple example

User event on Kafka:

- **JSON:** easy to debug in console; larger; silent field drift until runtime bugs.
- **Avro + Schema Registry:** compact; incompatible schema rejected at produce time; consumers evolve safely.
- **Protobuf:** great for service-to-service; less common as the long-term lake format than Avro/Parquet.

At rest for analytics: **Parquet/ORC** (columnar) beat row JSON for warehouse scans.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| JSON | Ubiquity, debuggability | Size, weak typing, costly parse |
| Protobuf | Speed, strict contracts | Tooling; less friendly ad-hoc |
| Avro + registry | Safe pipeline evolution | Infra + discipline |
| Schema-less “flexibility” | Ship fast | Poison data, broken consumers |

## Pitfalls

- **No plan for evolution** — first field rename breaks three consumers.
- **Dumping Protobuf into a data lake forever** without a documented compatibility story.
- **Enums / unions** changed carelessly (Avro/Protobuf have sharp edges).
- **Floating money in JSON** — use integer cents or decimals carefully.
- **Assuming binary = always faster** — tiny JSON payloads + caching may not matter; measure at scale.

## Interview trigger phrase

> “I'd use **JSON for external APIs**, **Protobuf for internal RPC**, and **Avro with a schema registry** on Kafka — and I'd design for **backward-compatible** field evolution from day one.”

## Exercise

You add a required `currency` field to an existing Kafka payment event consumed by three services on different release trains. Why is “required” dangerous, and what safer change do you ship first?
