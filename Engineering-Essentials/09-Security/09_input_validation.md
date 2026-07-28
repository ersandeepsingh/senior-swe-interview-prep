# Input Validation & Sanitization

> Treat all external input as **hostile**. **Validate** at trust boundaries (type, length, format, range); **encode/sanitize** on the way out for the right context (HTML, SQL, shell). Never rely on the client alone.

## Plain English

| Term | Meaning |
|------|---------|
| **Validation** | Accept only well-formed expected data (reject early) |
| **Sanitization** | Transform/clean data (dangerous if used instead of encoding) |
| **Output encoding** | Escape for HTML/JS/URL/SQL context |
| **Trust boundary** | Where data crosses from untrusted → trusted (HTTP, queue, file) |

```text
  Client JSON → validate schema → business logic → encode for HTML/DB
       ▲                                              │
       └── never trust ───────────────────────────────┘
```

**Allowlists beat denylists.** Prefer “email must match this shape / enum must be one of …” over “block `<script>`.”

## Essentials (must-know for this topic)

### Validation vs sanitization vs encoding

| Term | Meaning | When |
|------|---------|------|
| **Validation** | Accept only expected shape (reject early) | Trust boundary in |
| **Sanitization** | Clean/transform input | Risky as sole defense; use vetted libs for HTML subsets |
| **Output encoding** | Escape for HTML/JS/URL/SQL context | On the way **out** |

### Trust boundaries

| Boundary | Example |
|----------|---------|
| HTTP request | Query, body, headers, cookies |
| Queue / event | “Internal” messages still need schema checks |
| File upload | Size, type sniff, store outside web root |
| Logs | Newlines in usernames → log injection |

### Rules that belong in every answer

| Rule | Why |
|------|-----|
| **Allowlist > denylist** | Attackers bypass “block DROP/script” |
| **Parameterized queries** | Stops SQLi; don’t splice `sort` columns — allowlist them |
| **Encode for context** | HTML ≠ URL ≠ shell escaping |
| **Client validation = UX only** | Security is server-side |

## Simple example

**Create user API:**

```text
  email:    format + max 320 chars
  age:      integer 0..150
  role:     enum [user] only (ignore client-sent admin)
  bio:      max 500; store raw; encode on render
  orderBy:  allowlist columns — never splice raw into SQL
```

**File upload:** check size, MIME sniff, extension allowlist, store outside web root, scan; don’t trust `Content-Type` alone.

## When to use / trade-offs

| Prefer **schema validation at edge** when… | Prefer **deeper domain validation** when… |
|--------------------------------------------|-------------------------------------------|
| Malformed traffic should die ASAP | Rules need DB state (“email unique”) |
| OpenAPI / JSON Schema available | Business invariants |

| Prefer **encode on output** when… | Prefer **sanitize HTML** when… |
|-----------------------------------|--------------------------------|
| Most user text display | You must allow a subset of HTML (editors) — use a vetted library |

| Decision | You gain | You give up |
|----------|----------|-------------|
| Strict schemas | Fewer weird states | Flexibility / versioning work |
| Normalize then validate | Cleaner data | Can hide attacks if done wrong |
| Strip “bad” characters | Feels safe | Bypass-prone; breaks legit input |

## Pitfalls

- Validating only in the UI.  
- String-building SQL/shell/LDAP from input.  
- Log injection via unchecked newlines in usernames.  
- Unicode / homoglyph surprises in allowlists.  
- Double-decoding bugs (`%252e%252e` path traversal).  
- Trusting queue messages from “internal” producers without schema checks.

## Interview trigger phrase

> “I’d **validate allowlists at every trust boundary**, bind parameters for queries, and **encode on output** for the right context — client checks are UX only, never security.”

## Exercise

**Search endpoint: `q`, `sort`, `page`.**

1. What validation on each?  
2. How does a bad `sort` become SQLi?  
3. Results rendered in HTML — where does encoding happen, and what if an API client wants JSON only?
