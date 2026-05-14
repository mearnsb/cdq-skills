# Quick Start: Bulk Table Onboarding

**TL;DR**: 3 phases × 200 tables = 2,000 rules. Estimated time: 3-4 hours.

---

## ⚡ Quick Reference

### Setup (One-Time)
```bash
# Generate list of all tables with suggested rules
python scripts/bulk_onboard_loop.py --schema samples --action generate-manifest --limit 200
```

Output: `onboarding-manifest.json` (ready for execution)

---

## 🔄 Per Table Workflow (3 Phases)

### Phase 1: Preview (30 seconds)
```bash
/cdq-run-sql --sql "SELECT * FROM samples.{TABLE} LIMIT 5"
```
✓ Confirms table exists, shows schema

### Phase 2: Register (1 minute)
```bash
/cdq-run-dq-job --dataset "ONBOARD_CDQ_AUTO_samples.{TABLE}" --sql "SELECT * FROM samples.{TABLE} LIMIT 10000"
```
✓ Dataset created, baseline job run

### Phase 3: Add 10 Rules (5 minutes)
```bash
# Rule 1: NOT NULL check
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.{TABLE}" --name "rule1_not_null" --sql "SELECT * FROM samples.{TABLE} WHERE column1 IS NULL LIMIT 100"

# Rule 2: NOT NULL check (column 2)
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.{TABLE}" --name "rule2_not_null" --sql "SELECT * FROM samples.{TABLE} WHERE column2 IS NULL LIMIT 100"

# Rule 3: Duplicates
/cdq-save-rule --dataset "ONBOARD_CDQ_AUTO_samples.{TABLE}" --name "duplicates" --sql "SELECT * FROM samples.{TABLE} t1 WHERE (SELECT COUNT(*) FROM samples.{TABLE} t2 WHERE t1.* = t2.*) > 1 LIMIT 100"

# Rule 4-10: See BULK_ONBOARDING_RUNBOOK.md for template rules
```

**Total per table**: ~6-7 minutes

---

## 📊 Scale Math

- 200 tables
- 7 min per table
- **Total time: ~24 hours** (but parallelizable in batches)

**Parallel approach** (recommended):
- Batch 1: 50 tables (parallel) → 2 hours
- Batch 2: 50 tables (parallel) → 2 hours
- Batch 3: 50 tables (parallel) → 2 hours
- Batch 4: 50 tables (parallel) → 2 hours
- **Total elapsed: ~8-10 hours** with 4 parallel workers

---

## 🎯 Key Points

### Naming
- **Logical name** (for skills): `ONBOARD_CDQ_AUTO_samples.{table}`
- **Physical table** (in SQL): `samples.{table}`

### Limits
- Preview: `LIMIT 5`
- Job: `LIMIT 10000`
- Rule queries: `LIMIT 100`

### Rules (10 per table)
1. Nullability checks (2 rules)
2. Duplicates (1 rule)
3. Cardinality/enums (1 rule)
4. Format/length (2 rules)
5. Encoding/special chars (1 rule)
6. Quality summaries (2 rules)

---

## ✅ Verify

```bash
# Check dataset registered
/cdq-get-dataset --dataset "ONBOARD_CDQ_AUTO_samples.{TABLE}"

# Check rules saved
/cdq-get-rules --dataset "ONBOARD_CDQ_AUTO_samples.{TABLE}"

# Check job status
/cdq-get-jobs
```

---

## 📁 Documentation

- **Full Plan**: `BULK_ONBOARDING_PLAN.md`
- **Runbook**: `BULK_ONBOARDING_RUNBOOK.md` (detailed commands)
- **Implementation**: `IMPLEMENTATION_SUMMARY.md` (architecture)
- **Script**: `scripts/bulk_onboard_loop.py` (generator)

---

## 🚀 Go Time

```bash
# 1. Generate manifest
python scripts/bulk_onboard_loop.py --schema samples --action generate-manifest

# 2. Pick first table from manifest
# 3. Execute 3 phases (6-7 min)
# 4. Verify with /cdq-get-rules
# 5. Repeat for all tables

# OR: Run script for automated batch processing
```

---

## 💡 Tips

- **Faster**: Use automation script for batch of 50-100 tables
- **Safer**: Execute manually for first 5-10 tables, then batch the rest
- **Parallel**: Create 4 separate Claude instances, each handles 50 tables
- **Monitor**: Check progress with `python scripts/bulk_onboard_loop.py ... --action check-progress`

---

## ❌ Troubleshooting

| Issue | Fix |
|-------|-----|
| Dataset name error | Use exact format: `ONBOARD_CDQ_AUTO_samples.{table}` |
| Rule save fails | Check SQL syntax for your database |
| Empty preview | Table might be empty (skip to next) |
| Timeout | Already happens with LIMIT 10000; reduce if needed |

---

## 📈 Success Metrics

After completion:
- ✓ 200 datasets registered
- ✓ 2,000 rules created
- ✓ All datasets accessible via `/cdq-get-dataset`
- ✓ All rules visible via `/cdq-get-rules`
- ✓ First DQ jobs completed for all datasets
