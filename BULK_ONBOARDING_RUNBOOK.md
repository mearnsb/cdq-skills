# Bulk Onboarding Runbook

Complete execution guide for onboarding all tables in `samples` schema.

## Quick Start

### Prerequisites
- CDQ skills installed and working
- `/cdq-run-sql`, `/cdq-run-dq-job`, `/cdq-save-rule` all functional
- Ability to run skill commands

### Step 1: Generate Manifest (One-Time)

```bash
python scripts/bulk_onboard_loop.py --schema samples --action generate-manifest --limit 200
```

Output: `onboarding-manifest.json` with all 200 tables and suggested rules.

---

## Execution Flow (Per Table)

For each table in the manifest, execute this 3-phase workflow:

### Phase 1: DISCOVERY (Preview)

**Command**: Run SQL preview
```
/cdq-run-sql --sql "SELECT * FROM samples.{table} LIMIT 5"
```

**Expected Output**:
- Schema information (columns, types)
- 5 sample rows (or fewer if table has < 5 rows)
- Row count for the full table

**Action**: Review the data structure and note any obvious issues

---

### Phase 2: ONBOARDING (Register Dataset)

**Command**: Register dataset and run initial DQ job
```
/cdq-run-dq-job \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --sql "SELECT * FROM samples.{table} LIMIT 10000"
```

**Notes**:
- Logical name: `ONBOARD_CDQ_AUTO_samples.{table}` (use this exact format)
- Query: Uses physical table name `samples.{table}` with `LIMIT 10000`
- This registers the dataset and runs the first DQ job

**Expected Output**:
- Dataset registration confirmation
- Job execution result (likely 0 issues on first run)

---

### Phase 3: RULES (Save 10 Rules)

Execute these 10 rule save commands for each table:

#### Rule 1: Primary Key Column NOT NULL
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "primary_key_not_null" \
  --sql "SELECT * FROM samples.{table} WHERE {first_column} IS NULL LIMIT 100"
```

#### Rule 2: Second Column NOT NULL (if exists)
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "{second_column}_not_null" \
  --sql "SELECT * FROM samples.{table} WHERE {second_column} IS NULL LIMIT 100"
```

#### Rule 3: Duplicate Rows (Exact Match)
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "duplicate_rows_exact" \
  --sql "SELECT * FROM samples.{table} t1 WHERE (SELECT COUNT(*) FROM samples.{table} t2 WHERE t1.* = t2.*) > 1 LIMIT 100"
```

#### Rule 4: Cardinality Check (Low-Variance Columns)
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "cardinality_check" \
  --sql "SELECT {low_cardinality_column}, COUNT(*) as cnt FROM samples.{table} GROUP BY {low_cardinality_column} ORDER BY cnt DESC LIMIT 20"
```

#### Rule 5: Empty String Check
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "no_empty_strings" \
  --sql "SELECT * FROM samples.{table} WHERE {first_column} = '' OR TRIM({first_column}) = '' LIMIT 100"
```

#### Rule 6: Excessive Length Check
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "length_check" \
  --sql "SELECT * FROM samples.{table} WHERE LENGTH({first_column}) > 50000 OR LENGTH({first_column}) < 1 LIMIT 100"
```

#### Rule 7: Control Character Detection
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "no_control_chars" \
  --sql "SELECT * FROM samples.{table} WHERE {first_column} REGEXP '[\\x00-\\x08\\x0B-\\x0C\\x0E-\\x1F\\x7F]' LIMIT 100"
```

#### Rule 8: Whitespace-Only Values
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "no_whitespace_only" \
  --sql "SELECT * FROM samples.{table} WHERE REGEXP_LIKE({first_column}, '^\\s+$') LIMIT 100"
```

#### Rule 9: Null Distribution Summary
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "null_distribution" \
  --sql "SELECT COUNT(*) as total_rows, COUNT({first_column}) as non_null_count, SUM(CASE WHEN {first_column} IS NULL THEN 1 ELSE 0 END) as null_count FROM samples.{table}"
```

#### Rule 10: Data Quality Summary
```
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.{table}" \
  --name "data_quality_summary" \
  --sql "SELECT COUNT(*) as total_rows, COUNT(DISTINCT 1) as unique_rows FROM samples.{table}"
```

---

## Example: Complete Flow for Single Table (bbc_news)

### Phase 1: DISCOVERY
```
/cdq-run-sql --sql "SELECT * FROM samples.bbc_news LIMIT 5"
```

**Analysis Output**:
- 4 columns: body (text), title (text), filename (text), category (text)
- 2,225 total rows
- All columns text type

### Phase 2: ONBOARDING
```
/cdq-run-dq-job \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --sql "SELECT * FROM samples.bbc_news LIMIT 10000"
```

### Phase 3: RULES (10 commands)

1. Body NOT NULL
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "body_not_null" --sql "SELECT * FROM samples.bbc_news WHERE body IS NULL LIMIT 100"
```

2. Title NOT NULL
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "title_not_null" --sql "SELECT * FROM samples.bbc_news WHERE title IS NULL LIMIT 100"
```

3. Duplicate rows
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "duplicate_rows_exact" --sql "SELECT * FROM samples.bbc_news t1 WHERE (SELECT COUNT(*) FROM samples.bbc_news t2 WHERE t1.* = t2.*) > 1 LIMIT 100"
```

4. Category cardinality
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "category_values" --sql "SELECT category, COUNT(*) as cnt FROM samples.bbc_news GROUP BY category ORDER BY cnt DESC"
```

5. Empty body
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "no_empty_body" --sql "SELECT * FROM samples.bbc_news WHERE body = '' OR TRIM(body) = '' LIMIT 100"
```

6. Body length
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "body_length_check" --sql "SELECT * FROM samples.bbc_news WHERE LENGTH(body) > 50000 OR LENGTH(body) < 100 LIMIT 100"
```

7. Control characters
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "no_control_chars" --sql "SELECT * FROM samples.bbc_news WHERE body REGEXP '[\\x00-\\x08\\x0B-\\x0C\\x0E-\\x1F\\x7F]' LIMIT 100"
```

8. Whitespace only
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "no_whitespace_only" --sql "SELECT * FROM samples.bbc_news WHERE REGEXP_LIKE(body, '^\\s+$') LIMIT 100"
```

9. Null distribution
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "null_distribution" --sql "SELECT COUNT(*) as total, SUM(CASE WHEN body IS NULL THEN 1 ELSE 0 END) as body_nulls, SUM(CASE WHEN title IS NULL THEN 1 ELSE 0 END) as title_nulls FROM samples.bbc_news"
```

10. Data summary
```
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" --name "data_summary" --sql "SELECT COUNT(*) as rows, COUNT(DISTINCT category) as unique_categories FROM samples.bbc_news"
```

---

## Scaling to All Tables

### Option A: Automated Loop (Scripted)

Create a script that orchestrates the loop and reads from `onboarding-manifest.json`:

```python
# pseudo-code
for table in manifest["tables"]:
    # Phase 1: Preview (automatic)
    # Phase 2: Onboarding (skill execution)
    # Phase 3: Rules (10x skill execution)
```

### Option B: Manual Execution (For First Few Tables)

1. Copy the table name from `onboarding-manifest.json`
2. Copy the Phase 1-3 commands
3. Execute each phase
4. Track completion in a separate file

### Option C: Hybrid (Recommended)

1. Use the manifest to identify tables
2. Batch tables into groups of 10-20
3. For each group, execute all 3 phases manually
4. Use `/cdq-get-dataset` to verify registration
5. Use `/cdq-get-rules` to verify rule creation

---

## Verification

After completing tables, verify with:

```bash
# Check a dataset was created
/cdq-get-dataset --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news"

# Check rules were saved
/cdq-get-rules --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news"

# Check recent jobs
/cdq-get-jobs
```

---

## Troubleshooting

### Issue: "Dataset already exists"
**Solution**: Use `--dataset` with exact name including `ONBOARD_CDQ_AUTO_` prefix

### Issue: Rule save fails
**Solution**: Check that:
1. Dataset name matches exactly
2. SQL syntax is valid for your database
3. Physical table name (`samples.{table}`) is correct

### Issue: Empty preview results
**Solution**: Table might be empty or access restricted. Skip to next table.

### Issue: SQL query syntax error
**Solution**: Different databases use different SQL. Examples:
- BigQuery: `REGEXP_CONTAINS()` instead of `REGEXP()`
- PostgreSQL: `~` for regex matching
- MySQL: `REGEXP` keyword

Adapt rules based on your database.

---

## Completion Metrics

Track these for each table:
- ✓ Preview succeeded
- ✓ Onboarding succeeded (dataset registered)
- ✓ 10 rules saved
- ✓ No errors

Goal: All 200 tables with 10 rules each = 2,000 total rules saved.
