# CDQ Naming Reference

## Two Types of Names — Never Confuse Them

### Logical Dataset Name
A name YOU choose when registering a dataset in CDQ. It's a label inside the CDQ system.

- Examples: `MY_DATASET`, `CUSTOMER_ANALYSIS`, `CDQ_AUTO_samples.orders`
- Used by: `--dataset` in `run-dq-job`, `save-rule`, `get-rules`, `get-results`, `save-alert`, `get-alerts`, `get-dataset`

### Physical Table Name
The actual database table name. Used in SQL queries against your warehouse.

- Examples: `samples.orders`, `myproject.mydataset.mytable`
- Used by: `--sql` in `run-sql`, and inside all rule/job SQL strings

## The Rule

```
--dataset "MY_DATASET"                      ← logical name (CDQ label)
--sql "SELECT * FROM samples.orders ..."    ← physical name (real table)
```

Rule SQL always references the physical table, even though the rule is attached to a logical dataset:
```bash
cdq-save-rule --dataset "MY_DATASET" \
  --sql "SELECT * FROM samples.orders WHERE email IS NULL"
#                      ^^^^^^^^^^^^^^^^ physical table in SQL
```
