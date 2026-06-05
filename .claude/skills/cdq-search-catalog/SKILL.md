---
name: cdq-search-catalog
description: Search registered datasets in the Collibra DQ catalog. Requires --query (use "" for all). Returns LOGICAL dataset names to use with --dataset in other commands. Use when: (1) Finding available datasets, (2) Discovering dataset names and metadata, (3) Checking if a dataset already exists before creating, (4) Getting dataset connection info.
---

# CDQ Search Catalog

> **TL;DR:** Search registered CDQ datasets (logical names). Use `""` to list all. Results are logical names — use them in `--dataset` for other commands.

## Command

```bash
cdq search-catalog --query "search_term" [--limit N] [--connection CXN]
```

❌ `cdq search-catalog "customer"` — must use `--query` flag.  
✅ `cdq search-catalog --query "" --limit 100` — lists all datasets.

## Done

Run the command, report the results, and stop.
