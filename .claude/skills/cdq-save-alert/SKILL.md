---
name: cdq-save-alert
description: Create a new alert for a dataset in Collibra DQ. Requires --dataset (logical name), --name, --condition, and --email. Use when: (1) Creating email notifications for DQ score thresholds, (2) Setting up alerts for rule failures, (3) Configuring condition-based notifications, (4) Monitoring specific metrics.
---

# CDQ Save Alert

> **TL;DR:** Create an email alert that fires when a DQ condition is met after a job run.
>
> `--dataset` takes the **logical dataset name** (e.g., `MY_DATASET`). See [lib/NAMING.md](../lib/NAMING.md).

## Command

```bash
cdq save-alert \
  --dataset "MY_DATASET" \
  --name "Alert Name" \
  --condition "score < 90" \
  --email "team@company.com" \
  [--message "Custom message"]
```

**Help output:**
```
usage: cdq save-alert [-h] --dataset DATASET --name NAME --condition CONDITION
                      --email EMAIL [--message MESSAGE]

options:
  -h, --help            show this help message and exit
  --dataset DATASET     Dataset name
  --name NAME           Alert name
  --condition CONDITION
                        Alert condition
  --email EMAIL         Email address
  --message MESSAGE     Alert message
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--dataset` | **Logical dataset name** in CDQ |
| `--name` | Alert name |
| `--condition` | Trigger condition (see below) |
| `--email` | Notification email address |
| `--message` | Optional custom message |

**Correct vs. incorrect usage:**
```
❌ cdq save-alert --dataset "MY_DATASET" --email "x@y.com"
   (WRONG — missing required --name and --condition)

❌ cdq save-alert --dataset "samples.orders" --name "a" --condition "score < 90" --email "x@y.com"
   (WRONG — --dataset must be a logical name, not a physical table)

✅ cdq save-alert --dataset "MY_DATASET" --name "Low Score" --condition "score < 90" --email "x@y.com"
   (correct)
```

## Condition Examples

| Condition | Meaning |
|-----------|---------|
| `score < 90` | Alert when DQ score drops below 90 |
| `rule_failed('my_rule')` | Alert when a specific rule fails |
| `completeness < 95` | Alert on completeness metric |

## Example

```bash
cdq save-alert \
  --dataset "MY_DATASET" \
  --name "Low Score Alert" \
  --condition "score < 85" \
  --email "dq-team@company.com"
```
