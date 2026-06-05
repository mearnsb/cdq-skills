---
name: cdq-list-tables
description: List physical tables in a database connection. All parameters optional. Use when: (1) User doesn't know what tables exist, (2) Exploring available tables in a schema, (3) Finding table names before creating datasets, (4) Searching tables by name pattern.
---

# CDQ List Tables

> **TL;DR:** List physical tables in the database. Results are physical table names — use them in SQL queries, not as CDQ dataset names.

## Command

```bash
cdq list-tables [--schema SCHEMA] [--search PATTERN] [--limit N] [--connection CXN]
```

❌ `cdq list-tables --dataset MY_DATASET` — no `--dataset` flag exists.

### Search Pattern Syntax

The `--search` parameter uses **SQL LIKE patterns** with `%` as the wildcard character:

- `--search "f%"` finds tables starting with "f" (e.g., `fact_sales`, `files`)
- `--search "%data"` finds tables ending with "data"
- `--search "%user%"` finds tables containing "user" anywhere

*Common mistake:* Using glob patterns like `f*` (with `*`) will not work — always use `%` as the wildcard.

## Done

Run the command, report the results, and stop. Do not call `run-sql` or explore further unless the user asks.
