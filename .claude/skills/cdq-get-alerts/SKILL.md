---
name: cdq-get-alerts
description: Retrieve alerts configured for a dataset in Collibra DQ. Requires --dataset with the LOGICAL dataset name (not a physical table name). Use when: (1) Viewing existing alerts for a dataset, (2) Checking alert conditions and notification settings, (3) Finding active/inactive alerts.
---

# CDQ Get Alerts

> **TL;DR:** List alerts attached to a dataset.
>
> `--dataset` takes the **logical dataset name** (e.g., `MY_DATASET`). See [lib/NAMING.md](../lib/NAMING.md).

## Command

```bash
cdq get-alerts --dataset "DATASET_NAME"
```

**Help output:**
```
usage: cdq get-alerts [-h] --dataset DATASET

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
❌ cdq get-alerts                          (WRONG — --dataset is required)
❌ cdq get-alerts "MY_DATASET"             (WRONG — must use --dataset flag)
✅ cdq get-alerts --dataset "MY_DATASET"   (correct)
```

## Example

```bash
cdq get-alerts --dataset "MY_DATASET"
```

## Output

JSON array of alerts with name, condition expression, email, and active status.
