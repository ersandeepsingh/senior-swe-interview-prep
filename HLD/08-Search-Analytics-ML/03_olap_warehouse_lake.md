# OLAP, Warehouse & Data Lake

> OLTP serves **transactions**; **OLAP / warehouses / lakes** serve **analytics** — scans, joins, and aggregates over huge history without killing the production DB.

## Plain English

Don’t run “GMV by country last 90 days” on the checkout primary. Separate **serving truth** from **analytical copies**.

| Store | Role |
|-------|------|
| **OLTP** | Row store, point reads/writes, current state |
| **Warehouse (OLAP)** | Columnar, SQL BI, governed schemas (Snowflake/BigQuery/Redshift) |
| **Data lake** | Cheap object storage of files (Parquet); flexible, needs governance |
| **Lakehouse** | Lake + table formats (Iceberg/Delta) ≈ warehouse features |

```text
  OLTP DBs ──CDC/ETL──►  Staging / Lake (Parquet)
                              │
                              ▼
                         Warehouse / Lakehouse
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
               Dashboards            ML training
               (Looker/Metabase)     feature batch jobs
```

## Simple example

Nightly/continuous pipeline loads order facts into a columnar warehouse; BI tools scan compressed columns. Ad-hoc data science reads Parquet in the lake; curated marts live in the warehouse.

```text
  Modeling sketch (star):
    fact_orders(date_key, user_key, gmv, ...)
    dim_user / dim_product / dim_geo
```

**Real-time analytics:** materialized views, ClickHouse/Druid, or streaming aggregates — when ops dashboards need seconds, not T+1 hours.

## Why prefer one over the other

| Prefer **warehouse** when… | Prefer **lake / lakehouse** when… |
|----------------------------|-----------------------------------|
| Strong SQL, BI, governance | Diverse raw formats; cheap retention |
| Predictable marts & SLAs | Heavy ML / unstructured + batch |
| Team lives in SQL | Engineers own Spark/Flink jobs |

**Freshness SLO:** say “BI lag < 15 min via CDC” explicitly. Batch ETL is fine for finance close; streaming for live ops.

## Trade-offs

| Decision | You gain | You give up |
|----------|----------|-------------|
| Separate OLAP | Protect OLTP; huge scans | Lag; dual pipelines |
| Lake only | Cost, flexibility | “Data swamp” without catalogs |
| Sync warehouse to prod | Fresh numbers | Load on source; complexity |
| Columnar storage | Fast aggregates | Weaker point-lookup vs OLTP |

**Trap:** Analytics queries on the primary. Seniors: **CDC out**, columnar store in, clear freshness SLO.

**Governance:** catalog (Hive/Glue/Unity), access control, and PII classification matter once the lake grows — interviewers like hearing “data product” not “dump S3.”

**Cost control:** partition by date, prune columns, avoid `SELECT *` scans — warehouses bill on bytes scanned.

## Interview trigger phrase

> “I’d keep OLTP clean and **CDC into a columnar warehouse/lakehouse** for BI — freshness target explicit, never ad-hoc scans on the primary.”

## Exercise

**Analytics for a food-delivery company.**

1. What lands in the lake vs curated warehouse marts?
2. Batch ETL vs streaming — when each for “live ops dashboard”?
3. One sentence on why columnar storage helps `SUM(gmv) GROUP BY city`.
