---
name: cdq-list-tables
description: List physical tables in a database connection. All parameters optional. Use when: (1) User doesn't know what tables exist, (2) Exploring available tables in a schema, (3) Finding table names before creating datasets, (4) Searching tables by name pattern.
---

# CDQ List Tables

> **TL;DR:** List physical tables in the database (queries INFORMATION_SCHEMA). Returns **physical table names** — use these in SQL queries, not as CDQ dataset names.

## Command

```bash
cdq list-tables [--schema SCHEMA] [--search PATTERN] [--limit N] [--connection CXN]
```

**Help output:**
```
usage: cdq list-tables [-h] [--schema SCHEMA] [--search SEARCH]
                       [--limit LIMIT] [--connection CONNECTION]

options:
  -h, --help            show this help message and exit
  --schema SCHEMA       Schema/dataset name (e.g., samples)
  --search SEARCH       Filter tables by name substring
  --limit LIMIT         Max tables to return (default: 20)
  --connection CONNECTION
                        Datasource connection name
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--schema` | $DQ_CXN default | Database schema/dataset to list |
| `--search` | none | Filter by name substring (`account` matches `%account%`) |
| `--limit` | 20 | Max tables to return |
| `--connection` | $DQ_CXN | Datasource connection name |

**Correct vs. incorrect usage:**
```
❌ cdq list-tables --dataset MY_DATASET    (WRONG — no --dataset flag exists)
❌ cdq list-tables --table orders          (WRONG — no --table flag exists)
✅ cdq list-tables --schema samples        (correct)
✅ cdq list-tables --search account        (correct — searches all schemas)
✅ cdq list-tables                         (correct — uses default schema)
```

## Examples

```bash
# List tables in a schema
cdq list-tables --schema samples

# Search for tables with "account" in the name
cdq list-tables --search account --limit 50
```

## Output

```json
{"tables": ["accounts", "customers", "orders"], "count": 3, "schema": "samples"}
```

> **Note:** If INFORMATION_SCHEMA is inaccessible, ask the user to provide a list of tables in CLAUDE.md or a `docs/tables.md` file.
