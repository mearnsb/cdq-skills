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

### Schema discovery and matching

If `--schema` is omitted and `DQ_SCHEMA` is unset, the command lists the connection's top-level schemas/databases instead of failing. Pick the exact, case-sensitive schema name from that response and pass it with `--schema`; `public` and `PUBLIC` can be different schemas.

Schema results and table results include `source: "explorer"` when they come from the DQ Explorer metadata endpoint. The Explorer path retrieves the full table list without the legacy SQL endpoint's approximate 250-row cap. If the connection alias is not accepted by Explorer, the command falls back to the legacy BigQuery `INFORMATION_SCHEMA.TABLES` query and labels the response `source: "sql-fallback"`.

### Search Pattern Syntax

The `--search` parameter is applied client-side using case-insensitive SQL `LIKE` semantics with `%` as the wildcard and `_` as a single-character wildcard:

- `--search "f%"` finds tables starting with `f`
- `--search "%data"` finds tables ending with `data`
- `--search "%user%"` finds tables containing `user` anywhere
- `--search "user"` is treated as `%user%` (substring match)

*Common mistake:* Using glob patterns like `f*` (with `*`) will not work — use `%` for wildcards.

## Done

Run the command, report the results, and stop. Do not call `run-sql` or explore further unless the user asks.
