# CDQ Skill Sequencing Checklist

For non-interactive workflows, batch processing, and automation using individual CDQ skills in combination.

---

## When to Use This vs. `/auto-cdq`

| Scenario | Use Sequencing Checklist | Use `/auto-cdq` |
|----------|---|---|
| Single dataset, exploratory | ❌ | ✅ |
| Multiple datasets, batch process | ✅ | ❌ |
| Want to loop/modify/explore in real-time | ❌ | ✅ |
| Headless/automation/CI-CD/scripting | ✅ | ❌ |
| Need user guidance and validation | ❌ | ✅ |
| Running in cron job or pipeline | ✅ | ❌ |
| Single dataset, quick validation | ✅ | ❌ |

**Key Distinction**:
- **Interactive (`/auto-cdq`)**: User paces the workflow, explores alternatives, sees multi-section headers
- **Skill Sequencing**: Headless execution, predetermined parameters, batch processing

---

## Common Sequences

### 1. Discovery Sequence
**Goal**: Find and validate a table before onboarding

**Steps**:
```
1. ☐ Test Connection
   Skill: /cdq-test-connection
   Check: Connection working, credentials valid

2. ☐ List Available Tables
   Skill: /cdq-list-tables --schema {schema} --limit 20
   Check: Table exists in schema, row count reasonable

3. ☐ Preview Data
   Skill: /cdq-run-sql --sql "SELECT * FROM `{schema}.{table}` LIMIT 5"
   Check: Schema matches expectations, data types correct, no obvious issues

4. ☐ Validate Row Count
   Skill: /cdq-run-sql --sql "SELECT COUNT(*) as cnt FROM `{schema}.{table}`"
   Check: Row count within expected range (not 0, not 100M+)

5. ☐ Ready for Onboarding
   Decision: Proceed to onboarding or try different table
```

**Safety Limits**:
- Preview: LIMIT 5 (fast, no performance impact)
- Analysis: LIMIT 100 (small sample, safe)
- Production: LIMIT 10,000-50,000 (depends on table size)

**Error Handling**:
- Connection fails → Stop, verify credentials in `.env`
- Table not found → Verify schema and table name spelling
- Query timeout → Reduce LIMIT or add WHERE filter for date range

---

### 2. Onboarding Sequence
**Goal**: Register dataset and run initial DQ job

**Steps**:
```
1. ☐ Validate Row Count (from Discovery)
   Skill: /cdq-run-sql --sql "SELECT COUNT(*) FROM `{schema}.{table}`"
   Check: Decide LIMIT for onboarding (all rows, or sample?)

2. ☐ Test Connection
   Skill: /cdq-test-connection
   Check: Ready to run jobs

3. ☐ Run DQ Job
   Skill: /cdq-run-dq-job --dataset "{dataset_name}" --sql "SELECT * FROM `{schema}.{table}` LIMIT {limit}"
   Check: Job ID returned, status = SETUP or RUNNING

4. ☐ Get Results
   Skill: /cdq-get-results --dataset "{dataset_name}" --run-id "{run_id}"
   Check: Score >= 75% (pass threshold), no unexpected failures

5. ☐ Verify Dataset Registered
   Skill: /cdq-get-dataset --dataset "{dataset_name}"
   Check: Dataset active, rules count matches expectations
```

**Safety Limits**:
- Sample: 1,000-10,000 rows (quick onboarding, fast verification)
- Standard: 10,000-50,000 rows (good balance)
- Full: All rows (production onboarding, slower)

**Error Handling**:
- Job fails → Check logs, verify data accessibility, retry with smaller LIMIT
- Low score → Expected if new data, check rule-level failures
- No results → Job may still be running, check status with `cdq-get-jobs`

---

### 3. Rules Analysis Sequence
**Goal**: Analyze data and create quality rules

**Steps**:
```
1. ☐ Analyze Column Cardinality
   Skill: /cdq-run-sql --sql "SELECT col, COUNT(DISTINCT col) FROM `{schema}.{table}` GROUP BY col LIMIT 10"
   Check: Find columns with low cardinality (good for "allowed values" rules)

2. ☐ Analyze Nulls and Empties
   Skill: /cdq-run-sql --sql "SELECT COUNT(*), SUM(CASE WHEN col IS NULL THEN 1 END) FROM `{schema}.{table}`"
   Check: Find columns with null patterns (completeness rules)

3. ☐ Test Rule SQL (for each rule)
   Skill: /cdq-run-sql --sql "{rule_sql}"
   Check: Violations = expected count, rule logic correct

4. ☐ Save Rule
   Skill: /cdq-save-rule --dataset "{dataset_name}" --name "{rule_name}" --sql "{rule_sql}"
   Check: Rule saved, active = 1

5. ☐ Verify All Rules Saved
   Skill: /cdq-get-rules --dataset "{dataset_name}"
   Check: Count matches expected number of rules
```

**Safety Limits**:
- Analysis: LIMIT 10,000 (representative sample)
- Test: No limit (testing the rule logic itself)

**Error Handling**:
- Test returns high violations → May be legitimate data issues or rule too strict
- High violations on existing data → Save rule, then monitor with re-runs
- Rule save fails → Check SQL syntax, dataset exists, rule name unique

---

### 4. Batch Dataset Processing
**Goal**: Process multiple datasets through full workflow (discovery → onboarding → rules)

**Setup**:
```bash
# Input: List of tables
for table in {table1, table2, table3, ..., table100}
do
  echo "Processing $table..."

  # Phase 1: Discovery (3-5 min per table)
  # Phase 2: Onboarding (5-10 min per table, depends on row count)
  # Phase 3: Rules (5-15 min per table)

  # Log results
  echo "$table: SUCCESS" >> results.log
done

# Output: Summary report
```

**Per-Table Steps**:
```
FOR EACH table:
  1. ☐ Discovery Sequence (validate table exists)
  2. ☐ Onboarding Sequence (register + run DQ job)
  3. ☐ Rules Analysis Sequence (analyze + save rules)
  4. ☐ Log results (success/failure, metrics)

AFTER all tables:
  1. ☐ Generate summary report (X succeeded, Y failed)
  2. ☐ Identify failures and reasons
  3. ☐ Re-run failures with diagnostics
```

**Safety Limits** (for batch):
- Preview: LIMIT 5 (fast checking)
- Onboarding: LIMIT 10,000 (reasonable sample for batch)
- Rules: LIMIT 5,000-10,000 (fast analysis)

**Batch-Specific Considerations**:
- Parallel vs. Sequential: Run sequentially to avoid rate limits
- Checkpoint: Test first table manually before running 100
- Logging: Write every result to file for audit trail
- Retry: Capture failures, re-run with investigation
- Duration: Estimate 15-30 min per table, plan accordingly

**Error Handling**:
- Transient failures (timeout) → Retry with longer timeout
- Data issues (table empty) → Log and skip, continue batch
- Connection drops → Restart from last successful table using checkpoint

---

## Universal Safety Checklist

Apply to ANY workflow using these skills:

```
Connection & Setup:
  ☐ DQ_URL, DQ_USERNAME, DQ_PASSWORD set in .env
  ☐ Connection tested: /cdq-test-connection succeeds
  ☐ Schema accessible: /cdq-list-tables returns results

SQL Queries:
  ☐ All queries have LIMIT clauses (except COUNT aggregates)
  ☐ Test with LIMIT 5 or LIMIT 100 before full queries
  ☐ Add date filters for large tables (WHERE date >= '2025-01-01')
  ☐ No SELECT * on tables with 100M+ rows

Rules:
  ☐ Test rule WHERE clause before saving (/cdq-run-sql)
  ☐ Check violations are reasonable (0, not 100M)
  ☐ Verify rule SQL syntax is correct (no typos)
  ☐ Save rules one at a time with error checks

Onboarding:
  ☐ Preview table schema first (SELECT * LIMIT 5)
  ☐ Validate row count (not 0, not impossibly large)
  ☐ Decide appropriate LIMIT before running job
  ☐ Check job results (score >= 75% minimum)

Verification:
  ☐ After saving: Verify with /cdq-get-*
  ☐ After onboarding: Check /cdq-get-results
  ☐ After rules: Confirm /cdq-get-rules shows all
  ☐ Before next step: Wait for previous job to complete
```

---

## Error Handling by Skill

### cdq-test-connection
| Error | Cause | Fix |
|-------|-------|-----|
| Connection refused | Wrong URL or server down | Verify DQ_URL in .env, check server status |
| Authentication failed | Wrong credentials | Verify DQ_USERNAME, DQ_PASSWORD, DQ_ISS |
| Timeout | Network slow | Increase timeout, check network |

### cdq-list-tables
| Error | Cause | Fix |
|-------|-------|-----|
| No tables returned | Schema empty or doesn't exist | Verify schema name, check with your DBA |
| Timeout | Large INFORMATION_SCHEMA | Reduce --limit or add --search filter |
| Access denied | No read access to schema | Check user permissions |

### cdq-run-sql
| Error | Cause | Fix |
|-------|-------|-----|
| Query timeout | Query too slow, data too large | Add LIMIT, add WHERE filter, reduce scope |
| Syntax error | Invalid SQL | Check SQL syntax, test locally first |
| No results | Query returns nothing | Check table name, schema, WHERE conditions |
| Memory error | Query too large | Add LIMIT, reduce columns, sample data |

### cdq-run-dq-job
| Error | Cause | Fix |
|-------|-------|-----|
| Job fails immediately | Invalid query or schema | Verify SQL with /cdq-run-sql first |
| Job timeout | Taking too long (large table) | Reduce LIMIT, add date filter |
| Dataset exists | Name already in use | Use different dataset name or overwrite intentionally |

### cdq-save-rule
| Error | Cause | Fix |
|-------|-------|-----|
| Rule syntax error | Invalid SQL or WHERE clause | Test with /cdq-run-sql first |
| Duplicate rule | Same name exists | Use different name or update existing |
| Dataset not found | Onboarding didn't complete | Run /cdq-run-dq-job first |

### cdq-get-results
| Error | Cause | Fix |
|-------|-------|-----|
| Results not available | Job still running | Wait 30-60 seconds, try again |
| No results found | Wrong dataset or run-id | Verify both parameters match |
| Empty array | Job completed but no output | Check job status with /cdq-get-jobs |

---

## Example: Processing 100 Datasets

### Setup
```bash
#!/bin/bash
SCHEMA="samples"
TABLES=("table1" "table2" ... "table100")
LOG_FILE="batch_results_$(date +%Y%m%d_%H%M%S).log"

echo "Starting batch processing at $(date)" >> $LOG_FILE
```

### Discovery Phase (Per Table)
```bash
for table in "${TABLES[@]}"; do
  echo "[$table] Discovery..." >> $LOG_FILE

  # Test connection (once, at start)
  if [[ $i -eq 0 ]]; then
    python lib/client.py test-connection || {
      echo "[$table] FAILED: Connection error" >> $LOG_FILE
      continue
    }
  fi

  # List tables (validate schema)
  python lib/client.py list-tables --schema $SCHEMA --limit 1 > /dev/null || {
    echo "[$table] FAILED: Schema not accessible" >> $LOG_FILE
    continue
  }

  # Preview table
  python lib/client.py run-sql --sql "SELECT * FROM \`$SCHEMA.$table\` LIMIT 5" > /tmp/preview.json || {
    echo "[$table] FAILED: Table not found or error" >> $LOG_FILE
    continue
  }

  # Validate row count
  ROW_COUNT=$(python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM \`$SCHEMA.$table\`" | jq '.rows[0][0].colValue')
  echo "[$table] Discovery complete - $ROW_COUNT rows" >> $LOG_FILE
done
```

### Onboarding Phase (Per Table)
```bash
for table in "${TABLES[@]}"; do
  echo "[$table] Onboarding..." >> $LOG_FILE

  DATASET="AUTO_CDQ_${SCHEMA}_${table}"
  LIMIT=10000

  # Run DQ job
  python lib/client.py run-dq-job \
    --dataset "$DATASET" \
    --sql "SELECT * FROM \`$SCHEMA.$table\` LIMIT $LIMIT" > /tmp/job.json || {
    echo "[$table] FAILED: Job registration error" >> $LOG_FILE
    continue
  }

  # Get results
  sleep 5  # Wait for job to complete
  python lib/client.py get-results \
    --dataset "$DATASET" \
    --run-id "$(date +%Y-%m-%d)" > /tmp/results.json || {
    echo "[$table] FAILED: Results retrieval error" >> $LOG_FILE
    continue
  }

  SCORE=$(jq '.score' /tmp/results.json)
  echo "[$table] Onboarded - Score: $SCORE" >> $LOG_FILE
done
```

### Rules Phase (Per Table)
```bash
for table in "${TABLES[@]}"; do
  echo "[$table] Rules..." >> $LOG_FILE

  DATASET="AUTO_CDQ_${SCHEMA}_${table}"
  LIMIT=5000

  # Analyze: Null patterns
  python lib/client.py run-sql \
    --sql "SELECT COUNT(*), SUM(CASE WHEN id IS NULL THEN 1 END) as nulls FROM \`$SCHEMA.$table\` LIMIT 1" \
    > /tmp/nulls.json

  # Test & Save: id_not_null
  python lib/client.py run-sql \
    --sql "SELECT * FROM \`$SCHEMA.$table\` WHERE id IS NULL" > /tmp/violations.json
  VIOLATIONS=$(jq '.rowCount' /tmp/violations.json)

  if [[ $VIOLATIONS -eq 0 ]]; then
    python lib/client.py save-rule \
      --dataset "$DATASET" \
      --name "id_not_null" \
      --sql "SELECT * FROM \`$SCHEMA.$table\` WHERE id IS NULL" || {
      echo "[$table] FAILED: Rule save error" >> $LOG_FILE
      continue
    }
    echo "[$table] Rule 'id_not_null' saved ($VIOLATIONS violations)" >> $LOG_FILE
  else
    echo "[$table] Rule 'id_not_null' skipped ($VIOLATIONS violations found)" >> $LOG_FILE
  fi
done
```

### Summary Report
```bash
# Count results
SUCCESS=$(grep -c "complete\|Onboarded\|saved" $LOG_FILE)
FAILED=$(grep -c "FAILED" $LOG_FILE)
TOTAL=${#TABLES[@]}

echo ""
echo "=== BATCH PROCESSING SUMMARY ===" >> $LOG_FILE
echo "Total tables: $TOTAL" >> $LOG_FILE
echo "Successful: $SUCCESS" >> $LOG_FILE
echo "Failed: $FAILED" >> $LOG_FILE
echo "Completion: $(( SUCCESS * 100 / TOTAL ))%" >> $LOG_FILE

echo ""
echo "FAILED TABLES:" >> $LOG_FILE
grep "FAILED" $LOG_FILE >> $LOG_FILE

echo "Batch processing completed at $(date)" >> $LOG_FILE
cat $LOG_FILE
```

---

## Checkpoint Pattern for Large Batches

For 100+ tables, use checkpoints:

```bash
CHECKPOINT_FILE=".batch_checkpoint"

# Load checkpoint
if [[ -f $CHECKPOINT_FILE ]]; then
  LAST_TABLE=$(cat $CHECKPOINT_FILE)
  echo "Resuming from: $LAST_TABLE"
fi

for table in "${TABLES[@]}"; do
  # Skip until checkpoint
  if [[ -n "$LAST_TABLE" && "$table" != "$LAST_TABLE" ]]; then
    continue
  fi
  LAST_TABLE=""  # Found checkpoint, continue normally

  # Process table...

  # Save checkpoint
  echo "$table" > $CHECKPOINT_FILE
done

# Cleanup
rm $CHECKPOINT_FILE
```

**Benefits**:
- Resume after failures without reprocessing
- Monitor progress
- Easier debugging (know which table caused issue)

---

## References

- **Interactive Workflow**: See `docs/00_START_HERE_INTERACTIVE_WORKFLOW.md` for `/auto-cdq` usage
- **Individual Skills**: See `.claude/skills/cdq-*/SKILL.md` for detailed skill documentation
- **Memory**: See project memory for environment setup and configuration

---

**Version**: 2026-04-09
**Use**: Non-interactive, batch, automation, and scripting workflows
**Status**: Ready for production use

This checklist is designed for **headless execution** where skills are combined in predetermined sequences. For interactive exploration, use `/auto-cdq` instead.
