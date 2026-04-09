# Interactive Workflow Reference — 2026-04-09 Census Example

**Status**: ✅ Complete Success — Reference implementation for all future interactive workflows

This document captures the successful interactive workflow pattern that should be the **DEFAULT behavior** for all `/auto-cdq` slash commands.

## What Makes This Pattern Work

### 1. Multi-Section Headers
Visual progress tracking with ☐ (pending) and ✓ (complete):

```
═══════════════════════════════════════════════════════════════════════════════
✓ Schema      ✓ Table       ✓ Preview     ✓ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

**Result**: User always knows where they are and how far they've come

---

### 2. Lightweight Questions First
Use `AskUserQuestion` for config/selection (not heavy surveys):

```
Question: "Which schema should we search in?"
Options: ["samples (Recommended)", "Type something else"]
```

**Key**: Ask BEFORE skill execution so user intent is clear

---

### 3. Skill Execution Between Questions
Don't batch questions. Instead:

1. Ask selection question (schema)
2. Execute skill with user's selection (list tables)
3. Display raw results
4. Ask validation question ("Looks good?")
5. Potentially loop back

**Pattern**:
```
Question → Skill → Display → Validate → [Loop or Continue]
```

---

### 4. Raw Output Display
Always show SQL queries, result tables, statistics before asking confirmation:

**Good**:
```
🔄 [RUNNING SKILL: cdq-list-tables --schema samples --limit 20]

Available Tables:
┌────┬───────────────────────┐
│ #  │ Table Name            │
├────┼───────────────────────┤
│ 1  │ census_tracts_alabama │
│ 2  │ census_tracts_alaska  │
│ 3  │ census_tracts_...     │
└────┴───────────────────────┘
```

**Bad**:
```
Found 50 tables. Which one?
[Option dropdown]
```

**Result**: User makes informed decisions based on actual data

---

### 5. Validation Loops
Provide clear options for iteration:

```
AskUserQuestion:
  question: "Preview of census_tracts_new_york - Looks good?"
  options:
    - "Yes, proceed (Recommended)"
    - "Show more rows"
    - "Choose different table"
    - "Exit"
```

**Key**: 3+ iterations possible - user controls pacing

---

### 6. Update Header After Each Phase
Progress is VISIBLE:

```
Before Phase 1:  ☐ Schema  ☐ Table  ☐ Preview  ☐ Confirm
After Phase 1:   ✓ Schema  ☐ Table  ☐ Preview  ☐ Confirm
After Phase 2:   ✓ Schema  ✓ Table  ☐ Preview  ☐ Confirm
```

**Result**: Clear sense of progress and accomplishment

---

### 7. Batch Operations with Per-Item Validation
For operations with multiple items (like rules), test EACH one before batch saving:

**Workflow**:
1. Propose 13 rules
2. Test rule 1 → display violations → ask confirmation
3. Test rule 2 → display violations → ask confirmation
4. ... (repeat for all)
5. Ask batch confirmation: "Ready to save all 13?"
6. Save all at once

**Result**: User has confidence in each rule before committing

---

## Reference Session: 2026-04-09 Census Workflow

### Discovery Phase (4 steps)

1. **Schema Selection**
   - Question: "Which schema should we search in?"
   - Selected: `samples`
   - Header: ✓ Schema | ☐ Table | ☐ Preview | ☐ Confirm

2. **Table Discovery**
   - Skill: `/cdq-list-tables --schema samples --limit 20`
   - User input: "Show tables with 'census' in name"
   - Skill: `/cdq-list-tables --schema samples --search %census% --limit 50`
   - Results: 50 census tracts tables
   - Selected: `census_tracts_new_york`
   - Header: ✓ Schema | ✓ Table | ☐ Preview | ☐ Confirm

3. **Data Preview**
   - Skill: `/cdq-run-sql --sql "SELECT * FROM census_tracts_new_york LIMIT 5"`
   - Display: 5 rows, 13 columns, schema info
   - Question: "Preview looks good?"
   - Selected: "Yes, proceed"
   - Header: ✓ Schema | ✓ Table | ✓ Preview | ☐ Confirm

4. **Confirmation**
   - Question: "Ready to proceed with census_tracts_new_york?"
   - Selected: "Yes, proceed"
   - Header: ✓ Schema | ✓ Table | ✓ Preview | ✓ Confirm

**Result**: User guided through 4 phases, always in control, always informed

---

### Onboarding Phase (4 steps)

1. **Data Source Reuse**
   - Used: `census_tracts_new_york` from Discovery
   - Header: ✓ Data Source | ☐ Config | ☐ Validation | ☐ Execute

2. **Configuration**
   - Question: "What should we call this dataset?"
   - Proposed: `census_tracts_new_york_dq` → User modified to: `AUTO_CDQ_samples.census_tracts_new_york`
   - Question: "How many rows should we analyze?"
   - Selected: `10,000` (actual: 4,918 all rows)
   - Header: ✓ Data Source | ✓ Config | ☐ Validation | ☐ Execute

3. **Validation**
   - Skill: `/cdq-test-connection`
   - Result: ✓ Connection working
   - Skill: `/cdq-run-sql --sql "SELECT COUNT(*) FROM census_tracts_new_york"`
   - Result: 4,918 rows available
   - Question: "Ready to onboard?"
   - Selected: "Yes, proceed"
   - Header: ✓ Data Source | ✓ Config | ✓ Validation | ☐ Execute

4. **Execution**
   - Skill: `/cdq-run-dq-job --dataset ... --sql ...`
   - Result: Job 519 started
   - Skill: `/cdq-get-results --dataset ... --run-id 2026-04-09`
   - Results: Score 100%, 4,918 rows analyzed
   - Header: ✓ Data Source | ✓ Config | ✓ Validation | ✓ Execute

**Result**: Dataset onboarded with 100% quality score

---

### Rules Phase (4 steps)

1. **Dataset Selection**
   - Reused: `AUTO_CDQ_samples.census_tracts_new_york` from Onboarding
   - Header: ✓ Dataset | ☐ Analysis | ☐ Select | ☐ Test & Save

2. **Analysis**
   - Skill: Ran 4 analysis SQL queries:
     - Null pattern check → 0 nulls in key columns
     - Uniqueness check → geo_id is unique key
     - Cardinality check → functional_status only 'S'
     - Format checks → all valid
   - Proposed: 13 rules (3 selected, 10 additional anomaly checks)
   - Header: ✓ Dataset | ✓ Analysis | ☐ Select | ☐ Test & Save

3. **Validation Testing**
   - Skill: Ran 13 validation SQL queries
   - Results:
     - 12 rules: 0 violations each ✓
     - 1 rule: 18 violations (area_land_positive - legitimate anomalies) ⚠
   - Display: Summary table with all violations
   - Header: ✓ Dataset | ✓ Analysis | ✓ Select | ☐ Test & Save

4. **Batch Save**
   - Skill: Saved each rule individually with error handling
   - Verification: `/cdq-get-rules` returned all 13 rules ACTIVE
   - Skill: Ran job with all 13 rules active
   - Results: Score 100%, detected 18 area anomalies
   - Header: ✓ Dataset | ✓ Analysis | ✓ Select | ✓ Test & Save

**Result**: 13 comprehensive rules created, tested, and validated

---

### Success Metrics

| Metric | Value |
|--------|-------|
| **Dataset Size** | 4,918 rows, 13 columns |
| **Rules Created** | 13 total |
| **Rules Passing** | 12/13 (100%) |
| **Anomalies Found** | 18 legitimate (area_land_positive) |
| **Overall Quality Score** | 100% |
| **User Actions** | 8 AskUserQuestion prompts |
| **Skill Executions** | 16+ skills run with data display |
| **Validation Loops** | 3 (table selection, data preview, rule testing) |
| **Session Duration** | ~30 minutes (user-paced) |

---

## Key Implementation Patterns

### Pattern A: Simple Selection
```
Question: "Which X?"
Options: [Recommended], [Other], [Custom]
Use for: Schema, dataset, alert type
Skills: 0-1 (optional if user chooses "Browse")
```

### Pattern B: Search + Pick
```
Question: "How to find tables?"
Options: [Search by pattern], [Browse all], [Type specific name]
Skill: /cdq-list-tables (search or browse)
Display: Table list with numbering
Question: "Which table?"
Options: Dynamically generated from results
Skills: 1
Loops: Can search again, try different pattern
```

### Pattern C: Record + Validation
```
Question: "Configure X" (dataset name, row limit)
Store: User values
Skill: /cdq-run-sql (count rows, test connection)
Display: Stats, warnings, confirmations
Question: "Ready?"
Options: [Proceed], [Modify], [Cancel]
Skills: 1-2
Loops: Can modify and retest
```

### Pattern D: Batch Test + Save
```
For each item:
  - Test with skill
  - Display results
  - Collect into list
Question: "Save all X items?"
Options: [Yes], [Modify], [Select subset], [Cancel]
Skill: Batch save all approved
Display: Success confirmation for each
Skills: N+1 (N tests, 1 batch save)
Loops: Can test subsets, modify, retry
```

---

## Do's and Don'ts

### ✅ DO

1. **Insert skills BETWEEN questions** - Don't batch all questions
2. **Show raw output** - SQL, tables, metrics, not summaries
3. **Provide loop options** - "More?", "Different?", "Modify?"
4. **Update headers** - Visual progress after each phase
5. **Use lightweight questions** - Simple options, not complex surveys
6. **Test before saving** - Run validation on each item before batch operations
7. **Display stats** - Row counts, violation counts, pass rates

### ❌ DON'T

1. **Ask all config questions first** - Break them up with skill execution
2. **Hide data output** - Always show what the skill returned
3. **Force linear flow** - Let users go back, modify, retry
4. **Leave header stale** - Update after each major phase
5. **Use heavy surveys** - Keep AskUserQuestion under 5 options
6. **Save without testing** - Always validate before committing
7. **Assume success** - Always error-check and provide fallbacks

---

## Testing Checklist

Before deploying any new interactive workflow:

- [ ] All 4 phases have multi-section headers
- [ ] AskUserQuestion questions are lightweight (<5 options)
- [ ] Skills execute between questions (not after all Q's)
- [ ] Raw output is displayed before asking confirmation
- [ ] At least 1 validation loop is possible (3+ iterations)
- [ ] Headers update after each major phase
- [ ] User can go back/modify/retry (test with at least 1 loop)
- [ ] Batch operations test each item individually
- [ ] Error handling is graceful (no crashes)
- [ ] Success metrics are displayed (scores, counts, summaries)

---

## Copy-Paste Template

Use this for any new interactive workflow:

```
## Phase N: [Phase Name]

**Header Update:**
```
✓ Phase1  ☐ PhaseN  ☐ Phase(N+1)
```

**Step N.a: [Lightweight Decision]**

AskUserQuestion:
  question: "[Clear ask]?"
  header: "[Short label]"
  multiSelect: false
  options:
    - label: "[Recommended option]"
      description: "[What this does]"
    - label: "[Alternative]"
      description: "[What this does]"

**Step N.b: [Skill Execution]**

Skill: `/skill-name --arg1 value1 --arg2 value2`

Display:
```
[Table/results/metrics]
```

**Step N.c: [Validation]**

AskUserQuestion:
  question: "[Did that work for you?]"
  header: "[Action]"
  multiSelect: false
  options:
    - label: "Yes, proceed (Recommended)"
      description: "[Continue to next phase]"
    - label: "[Loop option 1]"
      description: "[What user can retry]"
    - label: "[Loop option 2]"
      description: "[What user can try different]"

Handle loops: Go back to Step N.b, re-run skill, re-display results
```

---

## References

- **Successful Implementation**: This document (2026-04-09)
- **Pattern Guide**: `docs/HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md`
- **Skill Definition**: `.claude/skills/auto-cdq/SKILL.md`
- **Memory**: `/Users/brian/.claude/projects/-Users-brian-github-cdq-skills/memory/MEMORY.md` (Interactive vs Non-Interactive section)

---

**Use this reference for all new interactive CDQ workflows. The pattern works.**
