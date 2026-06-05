---
name: cdq-get-dataset
description: Retrieve dataset configuration and metadata from Collibra DQ. Requires --dataset with the LOGICAL dataset name (not a physical table name). Use when: (1) Getting dataset definition details, (2) Finding connection settings, (3) Viewing source query for a dataset, (4) Checking schedule information.
---

# CDQ Get Dataset

> **TL;DR:** Retrieve the registered definition for a dataset — connection, source SQL, schedule, and profile settings. `--dataset` = logical name (e.g. `MY_DATASET`), not a physical table.

## Command

```bash
cdq get-dataset --dataset "DATASET_NAME"
```

## Done

Run the command, report the results, and stop.
