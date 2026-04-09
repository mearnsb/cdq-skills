---
name: auto-cdq
description: 'Interactive CDQ workflows with visual progress tracking (Discovery, Rules, Onboarding)'
interaction: interactive
commands:
  - name: auto-cdq discovery
    description: 'Find and preview a table: schema → table → preview → confirm'
  - name: auto-cdq rules
    description: 'Create data quality rules: dataset → analyze → select rules → test & save'
---

# Auto-CDQ Discovery Workflow

Complete interactive workflow to discover and preview a data table.

## Implementation

Execute this workflow step-by-step:

### Initial Header
Print the progress header:
```
═══════════════════════════════════════════════════════════════════════════════
☐ Schema      ☐ Table       ☐ Preview     ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 1: Schema Selection

**Instruction:**
1. Print: `Phase 1: Schema Selection`
2. Use `AskUserQuestion` to ask: "Which schema should we search in?"
   - Option 1: "samples (Recommended)" - Use the samples demo schema
   - Option 2: "Type something else" - Enter a custom schema name
   - Option 3: "Chat about this" - Discuss schema options
3. Store user's schema choice
4. Update header to mark SCHEMA as complete (✓)

**Next Step:** Proceed to Phase 2

---

## Phase 2: Table Discovery

**Instruction:**
1. Print updated header:
```
═══════════════════════════════════════════════════════════════════════════════
✓ Schema      ☐ Table       ☐ Preview     ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

2. Print: `Phase 2: Table Discovery`

3. Use `AskUserQuestion` to ask: "How would you like to find a table in `{schema}`?"
   - Option 1: "Browse all tables" - List all tables in the schema
   - Option 2: "Search by pattern" - Search tables by name (e.g., %cust%)
   - Option 3: "Type specific table" - Enter a table name directly

4. **Based on user choice, execute skill:**
   - If "Browse all tables": Run `/cdq-list-tables --schema {schema} --limit 20`
   - If "Search by pattern": Ask for search pattern, then run `/cdq-list-tables --schema {schema} --search {pattern} --limit 20`
   - If "Type specific table": Ask for table name (store as-is, skip to Phase 3)

5. **Display the skill output** (JSON with list of tables)

6. If more than 3 tables shown, parse and format nicely:
   ```
   Available Tables:
   • CollibraEmployees (employee records)
   • Customer_MonthEnd (customer snapshots)
   • 311_service_requests (service logs)
   ... and more
   ```

7. Use `AskUserQuestion` to ask: "Which table would you like to work with?"
   - List top 3-5 tables as options
   - Add "Type something else" option
   - Add "Different search" option to go back

8. Store user's table choice

9. Update header to mark TABLE as complete (✓)

**Next Step:** Proceed to Phase 3

---

## Phase 3: Data Preview

**Instruction:**
1. Print updated header:
```
═══════════════════════════════════════════════════════════════════════════════
✓ Schema      ✓ Table       ☐ Preview     ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

2. Print: `Phase 3: Data Preview`

3. Print: `Query: SELECT * FROM `{schema}.{table}` LIMIT 5`

4. Execute skill: `/cdq-run-sql --sql "SELECT * FROM \`{schema}.{table}\` LIMIT 5"`

5. **Display results** in readable format:
   - Show column names from schema
   - Show first 5 rows as a formatted table
   - Show total row count if available

6. Use `AskUserQuestion` to ask: "Preview of `{schema}.{table}` - does this look right?"
   - Option 1: "Yes, use this table (Recommended)" - Proceed to Phase 4
   - Option 2: "Show more rows" - Re-run with LIMIT 20, ask again
   - Option 3: "Choose different table" - Go back to Phase 2 table selection
   - Option 4: "Chat about this" - Discuss the data

7. **If "Show more rows":**
   - Re-run: `/cdq-run-sql --sql "SELECT * FROM \`{schema}.{table}\` LIMIT 20"`
   - Display results
   - Ask validation question again (loop)

8. **If "Choose different table":**
   - Go back to Phase 2 step 3 (re-ask table selection)
   - **Do NOT** reset schema (keep it)

9. Mark PREVIEW as complete (✓) when user confirms

**Next Step:** Proceed to Phase 4

---

## Phase 4: Confirmation

**Instruction:**
1. Print updated header:
```
═══════════════════════════════════════════════════════════════════════════════
✓ Schema      ✓ Table       ✓ Preview     ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

2. Print: `Phase 4: Confirmation`

3. Use `AskUserQuestion` to ask: "Ready to proceed with `{schema}.{table}`?"
   - Option 1: "Yes, proceed (Recommended)" - Complete workflow
   - Option 2: "Go back" - Return to Phase 2
   - Option 3: "Exit" - Cancel and exit

4. **If "Go back":** Jump back to Phase 2 step 3 (table selection)

5. **If "Exit":** Print "Workflow cancelled." and end.

6. **If "Yes, proceed":** Mark CONFIRM as complete (✓)

---

## Completion

**Print final header:**
```
═══════════════════════════════════════════════════════════════════════════════
✓ Schema      ✓ Table       ✓ Preview     ✓ Confirm
═══════════════════════════════════════════════════════════════════════════════

🎉 DISCOVERY COMPLETE

Selected:
  Schema: {schema}
  Table: {table}

What's next?
```

Then ask: "What would you like to do next?"
- Option 1: "Run DQ job" → `/cdq-run-dq-job --dataset "{table}" --sql "SELECT * FROM \`{schema}.{table}\` LIMIT 10000"`
- Option 2: "Create rules" → `/cdq-workflow-suggest-rules --dataset "{table}"`
- Option 3: "Preview more data" → Run another `/cdq-run-sql`
- Option 4: "Exit" → End workflow

---

## Fallback: Onboarding Checklist

If at any point the user requests a simpler path or the workflow breaks, offer:

```
═══════════════════════════════════════════════════════════════════════════════
QUICK ONBOARDING CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

☐ Step 1: Pick a schema (e.g., "samples")
☐ Step 2: Pick a table (e.g., "CollibraEmployees")
☐ Step 3: Preview data with /cdq-run-sql
☐ Step 4: Run DQ job with /cdq-run-dq-job
☐ Step 5: View results with /cdq-get-results
```

Users can work through this checklist manually at their own pace using individual skills.

---

---

# Auto-CDQ Rules Workflow

Complete interactive workflow to create and test data quality rules for a dataset.

## Implementation

Execute this workflow step-by-step:

### Initial Header
Print the progress header:
```
═══════════════════════════════════════════════════════════════════════════════
☐ Dataset    ☐ Analysis    ☐ Select    ☐ Test & Save
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 1: Dataset Selection

**Instruction:**
1. Print: `Phase 1: Dataset Selection`
2. Use `AskUserQuestion` to ask: "Which dataset should we create rules for?"
   - Option 1: "Use recent analysis (if available)" - Use last discovered table
   - Option 2: "Search catalog" - Find existing dataset
   - Option 3: "Type something else" - Enter custom dataset name
3. Store user's dataset choice
4. Update header to mark DATASET as complete (✓)

**Next Step:** Proceed to Phase 2

---

## Phase 2: Data Analysis

**Instruction:**
1. Print updated header:
```
═══════════════════════════════════════════════════════════════════════════════
✓ Dataset    ☐ Analysis    ☐ Select    ☐ Test & Save
═══════════════════════════════════════════════════════════════════════════════
```

2. Print: `Phase 2: Data Analysis`

3. Execute skill: `/cdq-workflow-suggest-rules --dataset {dataset}`

4. **Display the skill output** with rule suggestions:
   ```
   Found 12 rule opportunities:

   HIGH Priority Rules:
   • id_not_null - Completeness check (0 violations)
   • id_uniqueness - Uniqueness check (0 violations)

   MEDIUM Priority Rules:
   • name_not_null - Completeness check (12 violations)
   • column_format - Format validation (3 violations)
   ```

5. Update header to mark ANALYSIS as complete (✓)

**Next Step:** Proceed to Phase 3

---

## Phase 3: Rule Selection

**Instruction:**
1. Print updated header:
```
═══════════════════════════════════════════════════════════════════════════════
✓ Dataset    ✓ Analysis    ☐ Select    ☐ Test & Save
═══════════════════════════════════════════════════════════════════════════════
```

2. Print: `Phase 3: Rule Selection`

3. Use `AskUserQuestion` to ask: "Which rules should we create?" (multiSelect: true)
   - List HIGH priority rules first (marked Recommended)
   - Then MEDIUM priority
   - Add "Select all HIGH priority (Recommended)" option
   - Add "Chat about this" option

4. Store user's rule selections

5. Update header to mark SELECT as complete (✓)

**Next Step:** Proceed to Phase 4

---

## Phase 4: Test & Save Rules

**Instruction:**
1. Print updated header:
```
═══════════════════════════════════════════════════════════════════════════════
✓ Dataset    ✓ Analysis    ✓ Select    ☐ Test & Save
═══════════════════════════════════════════════════════════════════════════════
```

2. Print: `Phase 4: Test & Save Rules`

3. **For each selected rule, execute test:**
   - Run `/cdq-run-sql --sql "{rule_query_test}"`
   - Display: "Testing rule X of Y: {rule_name}"
   - Show results: "Found N violations"

4. **After all tests pass, ask confirmation:**
   Use `AskUserQuestion`: "Ready to save N rules to dataset '{dataset}'?"
   - Option 1: "Yes, save all (Recommended)" - Save all tested rules
   - Option 2: "Review & modify" - Go back to Phase 3
   - Option 3: "Cancel" - Exit without saving

5. **If approved, save each rule:**
   - Execute: `/cdq-save-rule --dataset {dataset} --name "{rule_name}" --sql "{rule_sql}"`
   - Display: "Saving rule X of Y... ✓"

6. Update header to mark TEST & SAVE as complete (✓)

---

## Completion

**Print final header:**
```
═══════════════════════════════════════════════════════════════════════════════
✓ Dataset    ✓ Analysis    ✓ Select    ✓ Test & Save
═══════════════════════════════════════════════════════════════════════════════

🎉 RULES CREATED SUCCESSFULLY

Dataset: {dataset}
Rules Saved: N
Status: Ready for DQ job

Rules:
  1. {rule_name} ({priority}) - X violations
  2. {rule_name} ({priority}) - Y violations
```

Then ask: "What would you like to do next?"
- Option 1: "Run DQ job with new rules" → `/cdq-run-dq-job --dataset "{dataset}"`
- Option 2: "Create more rules" → Restart Phase 3
- Option 3: "View results" → `/cdq-get-results --dataset "{dataset}"`
- Option 4: "Exit" → End workflow

---

## Key Principles

- **Always show headers** at the start of each phase
- **Use AskUserQuestion** for all user choices (not prompts in text)
- **Execute skills** with actual /cdq-* commands for data
- **Display results** from skills in readable format
- **Allow loops** for validation (review, modify, etc.)
- **Update header** incrementally as phases complete
- **Be fault-tolerant** - if a skill fails, offer alternatives
- **Test before saving** - Always validate rule SQL before creating
