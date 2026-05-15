---
name: cdq-search-catalog
description: Search registered datasets in the Collibra DQ catalog. Requires --query (use "" for all). Returns LOGICAL dataset names to use with --dataset in other commands. Use when: (1) Finding available datasets, (2) Discovering dataset names and metadata, (3) Checking if a dataset already exists before creating, (4) Getting dataset connection info.
---

# CDQ Search Catalog

> **TL;DR:** Search **registered datasets** in CDQ (logical names like `MY_DATASET` or `CDQ_AUTO_samples.orders`). Use this to discover what exists before running jobs or saving rules.

## Command

```bash
cdq search-catalog --query "search_term" [--limit N] [--connection CXN]
```

**Help output:**
```
usage: cdq search-catalog [-h] --query QUERY [--limit LIMIT]
                          [--connection CONNECTION]

options:
  -h, --help            show this help message and exit
  --query QUERY         Search query
  --limit LIMIT         Max results
  --connection CONNECTION
                        Datasource connection name
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--query` | required | Search term — use `""` for all datasets |
| `--limit` | 50 | Max results |
| `--connection` | $DQ_CXN | Filter by connection |

**Correct vs. incorrect usage:**
```
❌ cdq search-catalog                          (WRONG — --query is required)
❌ cdq search-catalog "customer"               (WRONG — must use --query flag)
✅ cdq search-catalog --query "customer"       (correct)
✅ cdq search-catalog --query "" --limit 100   (correct — list all datasets)
```

## Examples

```bash
# List all registered datasets
cdq search-catalog --query "" --limit 100

# Find datasets matching "customer"
cdq search-catalog --query "customer"
```

## Output

Returns `dataAssetList` array. Key fields per dataset:
- `dataset` — logical dataset name (use this in `--dataset` for other skills)
- `ruleCnt` / `alertCnt` — rules and alerts attached
- `lastRun` — last job run timestamp
- `connectionName` — source connection
