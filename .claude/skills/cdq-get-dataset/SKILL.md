---
name: cdq-get-dataset
description: Retrieve dataset configuration and metadata from Collibra DQ. Requires --dataset with the LOGICAL dataset name (not a physical table name). Use when: (1) Getting dataset definition details, (2) Finding connection settings, (3) Viewing source query for a dataset, (4) Checking schedule information.
---

# CDQ Get Dataset

> **TL;DR:** Retrieve the registered definition for a dataset — connection, source SQL, schedule, and profile settings.
>
> `--dataset` takes the **logical dataset name** (e.g., `MY_DATASET` or `CDQ_AUTO_samples.orders`). See [lib/NAMING.md](../lib/NAMING.md).

## Command

```bash
cdq get-dataset --dataset "DATASET_NAME"
```

**Help output:**
```
usage: cdq get-dataset [-h] --dataset DATASET

options:
  -h, --help         show this help message and exit
  --dataset DATASET  Dataset name
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--dataset` | **Logical dataset name** registered in CDQ |

**Correct vs. incorrect usage:**
```
❌ cdq get-dataset                                  (WRONG — --dataset is required)
❌ cdq get-dataset "CDQ_AUTO_samples.orders"        (WRONG — must use --dataset flag)
✅ cdq get-dataset --dataset "CDQ_AUTO_samples.orders"  (correct)
✅ cdq get-dataset --dataset "MY_DATASET"           (correct)
```

## Example

```bash
cdq get-dataset --dataset "CDQ_AUTO_samples.orders"
```

## Output

JSON with dataset configuration: connection settings, source query, schedule, profile settings.
