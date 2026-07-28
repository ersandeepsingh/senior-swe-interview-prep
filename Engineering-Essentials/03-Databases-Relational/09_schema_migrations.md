# Schema Migrations

> Change the database schema **safely online**: expand/contract, stay backward compatible, and avoid long locks that take the site down.

## Plain English

A migration is a versioned script (Flyway, Liquibase, Rails/Django/Alembic/golang-migrate). In production you can’t stop the world — especially during rolling deploys when old and new app versions run together.

## Essentials (must-know for this topic)

### Expand / contract pattern

| Phase | What you do |
|-------|-------------|
| **1. Expand** | Add nullable column / new table; dual-write old+new |
| **2. Backfill** | Copy data outside a giant txn if needed |
| **3. Switch** | App reads from new column/path |
| **4. Contract** | Drop old column in a **later** release |

Keeps **old app instances** working mid-rollout.

### Safe vs risky changes (online)

| Safer online | Risky on large tables |
|--------------|------------------------|
| Add **nullable** column | Add `NOT NULL` without default/backfill |
| Additive indexes (`CREATE INDEX CONCURRENTLY`) | Rewrite whole table in one txn |
| New table / view | Rename casually while dual versions run |
| Widen type carefully | Drop column still read by old code |

### Compatibility during rolling deploys

| Rule | Why |
|------|-----|
| Backward-compatible migrations first | Old pods must still work |
| Don’t expand+contract in one deploy | Mid-deploy breakage window |
| App change may lag migration | Dual-write period |

### Postgres lock tip

`CREATE INDEX CONCURRENTLY` avoids long write locks (can’t run inside a transaction block). Prefer it on big tables.

## Why seniors get asked

Seniors own zero-downtime deploys. Interviewers listen for lock awareness and expand/contract — not just `ALTER TABLE` recklessly.

## Simple example

```sql
-- Step 1: expand (fast, safe)
ALTER TABLE users ADD COLUMN email_new TEXT;  -- nullable

-- Step 2: app writes email AND email_new; backfill
UPDATE users SET email_new = email WHERE email_new IS NULL;

-- Step 3: later — enforce NOT NULL after backfill; switch app to email_new

-- Step 4: contract
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN email_new TO email;
```

```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

## When to use / when not / trade-offs

| Safe online | Risky on large tables |
|-------------|------------------------|
| Add nullable column | Add `NOT NULL` without default/backfill |
| New index concurrently | Rewrite whole table in one txn |
| Additive views | Renaming casually during dual-running apps |

**Trade-offs:** multi-step migrations take longer to ship but avoid outages; big bang migrations are simpler and dangerous.

## Common pitfalls

- One migration that both breaks old code and new code mid-deploy
- Building indexes without `CONCURRENTLY` on huge tables
- No rollback plan / irreversible data loss
- Running heavy backfills in the migration txn

## Interview trigger phrase

> “I’d use expand/contract migrations, keep old app compatible during rollout, and create indexes concurrently on large tables.”

## Exercise

Rename `users.name` to `users.full_name` with zero downtime on a 100M-row table while rolling deploys run. List the migration steps and when the app changes.
