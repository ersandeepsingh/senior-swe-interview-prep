# Warehouse vs Lake vs Lakehouse

> Where analytical data lives. **OLTP** (app DB) ≠ **OLAP** (analytics). Warehouse, lake, and lakehouse are different bets on **schema, cost, and governance**.

## Plain English

**Why separate from OLTP?** Analytics scans crush transactional latency; schemas and retention differ; you want historical snapshots without locking prod.

```text
  OLTP Postgres  --CDC/ETL-->  Lake (raw JSON/Parquet)
                              --> curated Iceberg tables (lakehouse)
                              --> BI dashboards / ML features

  Or classic: OLTP --> ETL --> Warehouse (modeled star schema)
```

Small company: BigQuery/Snowflake alone may be enough — don't build a lake for resume-driven development.

## Essentials (must-know for this topic)

### Comparison

| Store | Idea | Typical tech |
|-------|------|--------------|
| **Data warehouse** | Curated, structured tables for BI/SQL; strong governance | Snowflake, BigQuery, Redshift |
| **Data lake** | Cheap object storage for raw + processed files | S3/ADLS + Spark; schema-on-read |
| **Lakehouse** | Lake storage + warehouse-like tables (ACID, versions) | Delta / Iceberg / Hudi on object storage |

### OLTP vs OLAP (don't mix)

| | OLTP | OLAP / analytics store |
|---|------|------------------------|
| Job | App transactions | Scans, aggregates, history |
| Shape | Normalized, current | Denormalized marts / facts |
| Risk if mixed | Analytics kills prod latency | — |

### Choose by need

| Prefer… | When |
|---------|------|
| **Warehouse-first** | SQL-heavy BI team, strong governance, moderate raw volume |
| **Lake-first** | Huge cheap retention, mixed formats, ML feature landing |
| **Lakehouse** | Want one copy of data + ACID/time travel on files |

**Swamp risk:** lake without catalog/quality/ownership → files nobody trusts.

## Simple example

E-commerce:

1. **Lake:** land raw clickstream + DB snapshots in S3 (cheap, retain years).
2. **Lakehouse tables:** `orders_clean` as Iceberg/Delta with schema + time travel.
3. **Warehouse marts** (or SQL endpoint on the lakehouse): `daily_revenue_by_region` for Looker.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Warehouse-first | Fast BI, governance | Cost at huge raw volume; less ideal for unstructured |
| Lake-first | Cheap retention, flexible formats | Swamp risk without catalogs/quality |
| Lakehouse | One copy of data, ACID on files | Platform maturity/ops; skills |
| Query prod OLTP for BI | “Simple” | Outages and wrong isolation for analytics |

## Pitfalls

- **Data swamp** — uncatalogued files nobody trusts.
- **No ownership / quality checks** — dashboards lie.
- **PII in the lake** without access controls and retention.
- **Duplicating the same curated data** in three tools with three truths.
- **Confusing lakehouse marketing with automatic governance** — you still need modeling discipline.

## Interview trigger phrase

> “I'd keep **OLTP separate**, land raw events in a **lake** for cost, and serve BI from **curated warehouse or lakehouse tables** with clear ownership and schema — not by querying prod.”

## Exercise

You have 50 TB of raw logs/year and a 20-person analytics team that lives in SQL. Do you start with warehouse, lake, or lakehouse — and what single risk do you mitigate first?
