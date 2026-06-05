---
name: cdq-run-sql
description: Execute SQL queries directly against the underlying datasource in Collibra DQ. Requires --sql with a PHYSICAL table name (e.g. schema.table) — never use logical CDQ dataset names here. Use when: (1) Testing source queries before creating datasets, (2) Exploring table schema and sample data, (3) Running ad-hoc queries for analysis, (4) Getting row counts.
---

# CDQ Run SQL

> **TL;DR:** Run SQL directly against your database. Always use **physical table names** (e.g., `samples.orders`) — never CDQ logical dataset names.

## Command

```bash
cdq run-sql --sql "SELECT * FROM samples.table LIMIT 10" [--connection CXN]
```

❌ `SELECT * FROM MY_DATASET` — logical names are not physical tables.  
❌ `SELECT * FROM samples.orders` without LIMIT — always add LIMIT for exploration.  
❌ `DESCRIBE samples.table` / `SHOW TABLES` — only SELECT statements are accepted.  
✅ `SELECT COUNT(*) FROM samples.orders` — aggregates don't need LIMIT.

## Done

Run the query, report the results, and stop. Do not call `list-tables` or any other command unless the user asks.
