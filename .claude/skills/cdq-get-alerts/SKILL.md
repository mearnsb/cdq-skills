---
name: cdq-get-alerts
description: Retrieve alerts configured for a dataset in Collibra DQ. Requires --dataset with the LOGICAL dataset name (not a physical table name). Use when: (1) Viewing existing alerts for a dataset, (2) Checking alert conditions and notification settings, (3) Finding active/inactive alerts.
---

# CDQ Get Alerts

> **TL;DR:** List alerts attached to a dataset. `--dataset` = logical name (e.g. `MY_DATASET`), not a physical table.

## Command

```bash
cdq get-alerts --dataset "DATASET_NAME"
```

## Done

Run the command, report the results, and stop.
