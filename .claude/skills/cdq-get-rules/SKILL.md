---
name: cdq-get-rules
description: Retrieve Data Quality rules configured for a dataset in Collibra DQ. Requires --dataset with the LOGICAL dataset name (not a physical table name). Use when: (1) Listing rules for a dataset, (2) Checking existing rule definitions, (3) Finding rule types and SQL expressions, (4) Verifying rules before saving new ones.
---

# CDQ Get Rules

> **TL;DR:** List DQ rules attached to a dataset. `--dataset` = logical name (e.g. `MY_DATASET`), not a physical table. Always run this before saving new rules to avoid duplicates.

## Command

```bash
cdq get-rules --dataset "DATASET_NAME" [--limit N]
```

## Done

Run the command, report the results, and stop.
