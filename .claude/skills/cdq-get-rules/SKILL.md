---
name: cdq-get-rules
description: Retrieve Data Quality rules configured for a dataset in Collibra DQ. Requires --dataset with the LOGICAL dataset name (not a physical table name). Use when: (1) Listing rules for a dataset, (2) Checking existing rule definitions, (3) Finding rule types and SQL expressions, (4) Verifying rules before saving new ones.
---

# CDQ Get Rules

> **TL;DR:** List DQ rules attached to a dataset. Always run this before saving new rules to avoid duplicates.
>
> `--dataset` takes the **logical dataset name** (e.g., `MY_DATASET`, `CDQ_AUTO_samples.orders`). See [lib/NAMING.md](../lib/NAMING.md).

## Command

```bash
cdq get-rules --dataset "DATASET_NAME" [--limit N]
```

**Help output:**
```
usage: cdq get-rules [-h] --dataset DATASET [--limit LIMIT]

options:
  -h, --help         show this help message and exit
  --dataset DATASET  Dataset name
  --limit LIMIT      Limit number of rules returned
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dataset` | required | **Logical dataset name** registered in CDQ |
| `--limit` | all | Max rules to return |

**Correct vs. incorrect usage:**
```
❌ cdq get-rules --dataset "samples.orders"      (WRONG only if samples.orders is a physical table, not registered in CDQ)
❌ cdq get-rules "MY_DATASET"                    (WRONG — must use --dataset flag)
✅ cdq get-rules --dataset "MY_DATASET"          (correct)
✅ cdq get-rules --dataset "CDQ_AUTO_samples.orders"  (correct — this is the logical name)
```

## Example

```bash
cdq get-rules --dataset "MY_DATASET"
```

## Output

JSON array of rules. Key fields per rule:
- `ruleNm` — rule name
- `ruleValue` — the SQL expression (references **physical** table)
- `ruleType` — type (e.g., `SQLF`)
- `isActive` — whether rule is active
