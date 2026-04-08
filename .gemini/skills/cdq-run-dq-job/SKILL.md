---
name: cdq-run-dq-job
description: Register a dataset definition and run a Data Quality job in Collibra DQ. Use when: (1) Running a new DQ job on a dataset, (2) Registering a new dataset with a logical name, (3) Re-running a job with updated rules, (4) Processing data with source SQL query.
---

# CDQ Run DQ Job

Register a dataset definition and run a Data Quality job.

> **Dataset Name vs Source SQL:**
> - `--dataset` is a **logical name** you assign (e.g., `MY_DATASET`, `DEMO_JOB`, `CUSTOMERS_2025`). This is how the dataset will be known in CDQ.
> - `--sql` contains the **actual source query** that pulls data from your database. Use real `schema.table` names here.

## Usage

```bash
python lib/client.py run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM actual_schema.actual_table WHERE condition = true" \
  --run-id "2025-03-09"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Logical dataset name (your choice, e.g., `MY_DATASET`) |
| `--sql` | Yes | Source SQL query (use actual schema.table names) |
| `--run-id` | No | Run ID/date (default: today's date YYYY-MM-DD) |
| `--connection` | No | Datasource connection name (default: $DQ_CXN) |

## Examples

```bash
# Create a dataset with a logical name
python lib/client.py run-dq-job \
  --dataset "CUSTOMER_ANALYSIS" \
  --sql "SELECT * FROM raw.customers WHERE active = true" \
  --run-id "2025-03-09"

# Use a descriptive logical name
python lib/client.py run-dq-job \
  --dataset "Q1_SALES_REVIEW" \
  --sql "SELECT * FROM sales.orders WHERE order_date >= '2025-01-01'"

# Complex source query
python lib/client.py run-dq-job \
  --dataset "ENRICHED_CUSTOMERS" \
  --sql "SELECT c.*, o.total_orders FROM customers c LEFT JOIN (SELECT customer_id, COUNT(*) as total_orders FROM orders GROUP BY customer_id) o ON c.id = o.customer_id"

# Run with specific connection
python lib/client.py run-dq-job \
  --dataset "SNOWFLAKE_DATA" \
  --sql "SELECT * FROM MY_SCHEMA.MY_TABLE" \
  --connection SNOWFLAKE
```

## Workflow

```
1. run-sql         → Test your source query with actual table names
2. run-dq-job      → Register dataset with logical name + run job
3. get-results     → Check the results
4. save-rule       → Add rules to the dataset (use logical name)
5. run-dq-job      → Run again to execute new rules
```

## Output

Returns JSON with:
- `registration` - Dataset definition registration result
- `job` - Job execution result

## API Endpoints

1. `PUT /v3/datasetDefs` - Register dataset definition
2. `POST /v3/jobs/run?dataset=<name>&runDate=<date>` - Run the job

## Notes

- The logical `--dataset` name is how you'll reference this dataset in all other commands
- Dataset names are unique within CDQ - reusing a name updates the definition
- Run ID is typically a date and is used to track different executions
- Profiling is enabled by default on new datasets