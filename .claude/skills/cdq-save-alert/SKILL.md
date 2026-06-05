---
name: cdq-save-alert
description: Create a new alert for a dataset in Collibra DQ. Requires --dataset (logical name), --name, --condition, and --email. Use when: (1) Creating email notifications for DQ score thresholds, (2) Setting up alerts for rule failures, (3) Configuring condition-based notifications, (4) Monitoring specific metrics.
---

# CDQ Save Alert

> **TL;DR:** Create an email alert that fires when a DQ condition is met. `--dataset` = logical name (e.g. `MY_DATASET`).

## Command

```bash
cdq save-alert --dataset "MY_DATASET" --name "Alert Name" --condition "score < 90" --email "team@company.com" [--message "msg"]
```

Common conditions: `score < 90`, `rule_failed('rule_name')`, `completeness < 95`

## Done

Run the command, report the result, and stop.
