# Bulk Table Onboarding Plan

## Overview
Systematically onboard all 100+ tables from `samples` schema into Collibra DQ with 10 data quality rules each.

**Naming Convention**: `ONBOARD_CDQ_AUTO_{schema}.{table}`
Example: `ONBOARD_CDQ_AUTO_samples.bbc_news`

## Architecture

### Phase 1: Loop Script (Python)
**File**: `scripts/bulk_onboard_loop.py`
**Purpose**: Orchestrate the onboarding process for all tables
**Inputs**: Table list from `cdq-list-tables`
**Outputs**: Progress tracking in `.onboarding-progress.json`

**Responsibilities**:
1. Load list of tables from samples schema
2. Read progress file to skip completed tables
3. For each pending table:
   - Get preview (LIMIT 5)
   - Extract schema information
   - Generate 10 rule suggestions based on column types/cardinality
   - Output JSON manifest for Claude to execute
   - Track completion
4. Handle failures gracefully (continue to next table)

### Phase 2: Rule Generation Logic
**Pattern-based rules for each table** (10 total):

1. **NULL/Empty Checks** (2 rules)
   - Rule 1: `column IS NULL` for each important-looking column
   - Rule 2: `column = ''` for string columns

2. **Cardinality/Enumeration** (2 rules)
   - Rule 3: Low-cardinality column validation (find columns with <20 distinct values)
   - Rule 4: High-cardinality key validation (find ID/key columns, check for duplicates)

3. **Duplicate Detection** (2 rules)
   - Rule 5: Exact duplicates (all columns)
   - Rule 6: Fuzzy duplicates (>90% match on key columns)

4. **Format/Pattern** (2 rules)
   - Rule 7: String length validation (too short/too long)
   - Rule 8: Special character validation (control chars, encoding issues)

5. **Data Quality** (2 rules)
   - Rule 9: Outlier detection (numeric columns, >3 std dev)
   - Rule 10: Unexpected values (empty after trim, whitespace-only)

### Phase 3: Skill Execution Pattern
**For each table:**

```
☐ DISCOVERY
   - Preview table (LIMIT 5)
   - Extract column info
   - Generate rule suggestions

✓ ONBOARDING
   - Run /cdq-run-dq-job with ONBOARD_CDQ_AUTO_{schema}.{table}
   - Query: SELECT * FROM {schema}.{table} LIMIT 10000

☐ RULES (10 per table)
   - Execute /cdq-save-rule × 10
   - Each rule uses the logical dataset name

STATUS: Repeat for all 100+ tables
```

## Workflow Steps

### Step 1: Generate Table Manifest
```bash
python scripts/bulk_onboard_loop.py --list-tables --schema samples
```

Output: `onboarding-manifest.json`
```json
{
  "tables": [
    {
      "name": "bbc_news",
      "schema": "samples",
      "logical_name": "ONBOARD_CDQ_AUTO_samples.bbc_news",
      "preview": {...},
      "suggested_rules": [...]
    }
  ],
  "total_tables": 102
}
```

### Step 2: For Each Table (Manual Execution via Skills)

**Template for single table (bbc_news)**:

#### ☐ DISCOVERY: Preview bbc_news
```bash
/cdq-run-sql --sql "SELECT * FROM samples.bbc_news LIMIT 5"
```

**Analysis**:
- Columns: body (text), title (text), filename (text), category (text)
- 2,225 total rows
- All columns are text/string type
- Category has low cardinality (likely few categories)

#### ✓ ONBOARDING: Register bbc_news
```bash
/cdq-run-dq-job \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --sql "SELECT * FROM samples.bbc_news LIMIT 10000"
```

#### ☐ RULES: Add 10 Rules for bbc_news

**Rule 1: NULL body check**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "body_not_null" \
  --sql "SELECT * FROM samples.bbc_news WHERE body IS NULL"
```

**Rule 2: NULL title check**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "title_not_null" \
  --sql "SELECT * FROM samples.bbc_news WHERE title IS NULL"
```

**Rule 3: Valid categories**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "valid_category_values" \
  --sql "SELECT * FROM samples.bbc_news WHERE category NOT IN ('tech','sport','business','politics','world')"
```

**Rule 4: Duplicate detection (exact match)**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "duplicate_articles_exact" \
  --sql "SELECT * FROM samples.bbc_news t1 WHERE EXISTS (SELECT 1 FROM samples.bbc_news t2 WHERE t1.body = t2.body AND t1.title = t2.title AND t1.rowid > t2.rowid)"
```

**Rule 5: Empty body check**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "body_not_empty" \
  --sql "SELECT * FROM samples.bbc_news WHERE TRIM(body) = '' OR LENGTH(TRIM(body)) < 100"
```

**Rule 6: Empty title check**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "title_not_empty" \
  --sql "SELECT * FROM samples.bbc_news WHERE TRIM(title) = '' OR LENGTH(TRIM(title)) < 5"
```

**Rule 7: Control characters in body**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "no_control_chars" \
  --sql "SELECT * FROM samples.bbc_news WHERE body REGEXP '[\\x00-\\x08\\x0B-\\x0C\\x0E-\\x1F\\x7F]'"
```

**Rule 8: HTML entities in text**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "no_html_entities" \
  --sql "SELECT * FROM samples.bbc_news WHERE body LIKE '%&#%' OR title LIKE '%&#%'"
```

**Rule 9: Excessive whitespace**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "no_excessive_whitespace" \
  --sql "SELECT * FROM samples.bbc_news WHERE body LIKE '%  %' OR REGEXP_LIKE(body, '\\n\\n\\n')"
```

**Rule 10: Filename format validation**
```bash
/cdq-save-rule \
  --dataset "ONBOARD_CDQ_AUTO_samples.bbc_news" \
  --name "valid_filename_format" \
  --sql "SELECT * FROM samples.bbc_news WHERE filename NOT LIKE 'bbc/%' OR filename NOT LIKE '%.txt'"
```

## Key Considerations

### Safety Limits
- **Row limit for jobs**: 10,000 (prevents huge datasets from overwhelming the system)
- **Preview limit**: 5 rows (quick validation)
- **Rules per table**: 10 (balanced coverage without excessive rules)
- **Total tables**: Process in batches if needed

### Rule Template Strategy
- **Rule 1-2**: Basic NOT NULL checks on key columns
- **Rule 3-4**: Cardinality-based validation (enum values, duplicate IDs)
- **Rule 5-6**: Duplicate row detection (exact and fuzzy)
- **Rule 7-8**: Format/encoding validation (control chars, HTML)
- **Rule 9-10**: Content quality (whitespace, text patterns)

### Naming Conventions
- **Logical Name**: `ONBOARD_CDQ_AUTO_{schema}.{table}` (used in `/cdq-run-dq-job` and `/cdq-save-rule`)
- **Physical Table**: `{schema}.{table}` (used in SQL queries: `SELECT * FROM {schema}.{table}`)
- **Rule Names**: Descriptive snake_case (e.g., `null_checks`, `duplicate_detection`)

### Error Handling
- If a table preview fails → skip to next table
- If onboarding fails → skip rules for that table, continue
- If a rule save fails → continue with next rule
- Progress tracked in `.onboarding-progress.json`

## Testing Approach

### Test Phase 1: Single Table (bbc_news)
1. Manual execution of all 3 phases
2. Verify preview works
3. Verify onboarding succeeds
4. Verify all 10 rules save correctly

### Test Phase 2: Small Batch (3 tables)
1. bbc_news (already tested)
2. austin_crime (similar structure)
3. bikeshare_trips (different structure)
4. Verify progress tracking

### Test Phase 3: Full Rollout
1. Run script on all 100+ tables
2. Monitor progress via `.onboarding-progress.json`
3. Handle failures as they arise
4. Generate completion report

## Progress Tracking

**File**: `.onboarding-progress.json`

```json
{
  "start_time": "2026-05-01T10:00:00Z",
  "last_updated": "2026-05-01T10:15:00Z",
  "completed": ["bbc_news", "austin_crime"],
  "in_progress": "bikeshare_trips",
  "failed": [],
  "pending": ["...all other tables"],
  "summary": {
    "total": 102,
    "completed": 2,
    "in_progress": 1,
    "pending": 99,
    "failed": 0
  }
}
```

## Execution Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|-----------------|
| Testing | Test 1 table + preview scripts | 30 min |
| Validation | Test 3-table batch | 45 min |
| Documentation | Create runbook for bulk execution | 30 min |
| Execution | Process all 100+ tables | 3-4 hours (can run in parallel) |
| Verification | Check results, fix failures | 1 hour |

## Next Steps

1. ✓ Create bulk_onboard_loop.py script
2. ✓ Test with bbc_news table
3. ✓ Test with 2-3 additional tables
4. Create runbook with exact commands
5. Execute full rollout
6. Generate completion metrics
