---
name: auto-cdq
description: 'Interactive guided CDQ workflow (Discovery → Onboarding → Rules). Hybrid Option 3: Multi-section progress headers + AskUserQuestion + skill execution with graceful non-interactive fallback.'
interaction: interactive
mode: user-guided
references:
  - see_also: docs/HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md
  - see_also: .claude/bin/auto-cdq-wizard.py for explicit non-interactive mode
commands:
  - name: auto-cdq
    description: Show workflow selection menu (Discovery, Onboarding, Rules)
  - name: auto-cdq discovery
    description: 'Discovery Workflow - Find and preview tables with schema selection, table discovery, data preview, and confirmation. Multi-section headers + skill execution.'
  - name: auto-cdq onboarding
    description: 'Onboarding Workflow - Register dataset and run DQ job with config validation (coming soon)'
  - name: auto-cdq rules
    description: 'Rules Workflow - Analyze data and create quality rules with per-rule testing (coming soon)'
---

# Auto-CDQ — Hybrid Progressive Disclosure Workflows

**Hybrid Option 3 Implementation**: Multi-section progress headers + AskUserQuestion + skill execution with graceful non-interactive fallback.

## Quick Start

```bash
# Interactive (Claude Code or terminal with stdin)
/auto-cdq discovery

# Non-interactive (explicit headless mode)
python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples --table accounts

# Orchestrator directly (internal implementation)
python3 .claude/bin/auto-cdq-orchestrator.py discovery
```

## Pattern: Hybrid Progressive Disclosure

Combines **multi-section header progress tracking** with **real skill execution** and **validation loops**. Users see professional wizard UX while controlling pacing and exploring alternatives with actual data from CDQ backend.

## Pattern Architecture

### Visual Foundation: Multi-Section Headers

Track progress with ☐ (pending) and ✓ (complete) checkmarks:

```
═══════════════════════════════════════════════════════════════════════════════
☐ Schema      ☐ Table       ☐ Preview     ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

As user progresses:

```
═══════════════════════════════════════════════════════════════════════════════
✓ Schema      ✓ Table       ☐ Preview     ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

### Core Pattern

1. **Print multi-section header** at start
2. **Ask lightweight questions** (via AskUserQuestion)
3. **Execute skills for data** (run /cdq-list-tables, /cdq-run-sql, etc.)
4. **Display raw output** (tables, SQL, results)
5. **Ask for validation** ("Looks good?", "More data?")
6. **Allow loops** (retry, modify, explore)
7. **Update header** (mark phase complete with ✓)

---

## Discovery Workflow

**Goal:** Find and preview a table, with guided schema and table selection

### Workflow Header

```
═══════════════════════════════════════════════════════════════════════════════
☐ Schema      ☐ Table       ☐ Preview     ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 1: Schema Selection (Lightweight)

**Type:** Lightweight decision

**Header Update:**
```
✓ Schema      ☐ Table       ☐ Preview     ☐ Confirm
```

**Implementation:**

1. Check `.env` for DQ_SCHEMA (configured schema)
2. Present schema options via AskUserQuestion:

```
AskUserQuestion:
  question: "Which schema should we search in?"
  header: "Schema"
  multiSelect: false
  options:
    - label: "samples (Recommended)"
      description: "Use the samples demo schema"
    - label: "Type something else"
      description: "Enter a custom schema name"
    - label: "Chat about this"
      description: "Discuss schema options"
```

3. Store selected schema
4. Mark Phase 1 complete (✓)

---

## Phase 2: Table Discovery (Interactive + Validation Loop)

**Type:** Interactive with skill execution and validation loop

**Header Update:**
```
✓ Schema      ☐ Table       ☐ Preview     ☐ Confirm
```

**Step 2a: Search or Browse**

Ask how to find tables:

```
AskUserQuestion:
  question: "How would you like to find a table?"
  header: "Table Discovery"
  multiSelect: false
  options:
    - label: "Search by pattern"
      description: "Search tables by name (e.g., %cust%)"
    - label: "Browse all tables"
      description: "List all tables in the schema"
    - label: "Type specific table"
      description: "Enter a table name directly"
```

**Step 2b: Execute cdq-list-tables Skill**

Based on user choice, run the skill:

```
For "Browse all tables":
  Run: /cdq-list-tables --schema {schema} --limit 20

For "Search by pattern":
  Ask: "Enter search pattern (SQL LIKE syntax):"
  Run: /cdq-list-tables --schema {schema} --search {pattern} --limit 20
```

**Display the raw output:**

```
🔄 [RUNNING SKILL: cdq-list-tables --schema "samples" --limit 20]

Available Tables (showing 20 of N):
┌────┬─────────────────────────────────┐
│ #  │ Table Name                      │
├────┼─────────────────────────────────┤
│ 1  │ CollibraEmployees               │
│ 2  │ Customer_MonthEnd               │
│ 3  │ 311_service_requests            │
│ 4  │ CurrencyScenario                │
└────┴─────────────────────────────────┘
```

**Step 2c: Ask User to Pick**

```
AskUserQuestion:
  question: "Which table would you like to work with?"
  header: "Select Table"
  multiSelect: false
  options:
    - label: "CollibraEmployees"
      description: "Employee records (1,234 rows)"
    - label: "Customer_MonthEnd"
      description: "Monthly customer snapshots (5,678 rows)"
    - label: "311_service_requests"
      description: "Service request logs (89,012 rows)"
    - label: "Type something else"
      description: "Enter a different table name"
```

3. Store selected table
4. Mark Phase 2 complete (✓)

---

## Phase 3: Data Preview (Validation Loop)

**Type:** Interactive with validation loop

**Header Update:**
```
✓ Schema      ✓ Table       ☐ Preview     ☐ Confirm
```

**Step 3a: Execute cdq-run-sql Skill**

Run preview:

```
Run: /cdq-run-sql --sql "SELECT * FROM `{schema}.{table}` LIMIT 5"
```

**Display the raw output:**

```
🔄 [RUNNING SKILL: cdq-run-sql]

Query:
  SELECT * FROM `samples.CollibraEmployees` LIMIT 5

Results (5 rows returned):
┌────┬───────────────┬──────────────┬─────────────┐
│ id │ name          │ department   │ start_date  │
├────┼───────────────┼──────────────┼─────────────┤
│ 1  │ Alice Johnson │ Engineering  │ 2020-01-15  │
│ 2  │ Bob Smith     │ Sales        │ 2019-06-01  │
│ 3  │ Carol White   │ Engineering  │ 2021-03-10  │
│ 4  │ David Brown   │ Finance      │ 2018-11-20  │
│ 5  │ Eve Davis     │ Sales        │ 2022-02-14  │
└────┴───────────────┴──────────────┴─────────────┘

Columns: id (int), name (string), department (string), start_date (date)
Total rows in table: 2,847 (showing 5)
```

**Step 3b: Ask for Validation**

```
AskUserQuestion:
  question: "Preview of `samples.CollibraEmployees`:\n\nColumns: id, name, department, start_date\n\nLooks good?"
  header: "Validate Preview"
  multiSelect: false
  options:
    - label: "Yes, use this table (Recommended)"
      description: "Proceed with this table"
    - label: "Show more rows"
      description: "See 20 rows instead of 5"
    - label: "Choose different table"
      description: "Go back to table selection"
    - label: "Chat about this"
      description: "Discuss the data"
```

**Step 3c: Handle Loops**

- If "Show more rows": Re-run cdq-run-sql with LIMIT 20, display again, ask again
- If "Choose different table": Go back to Phase 2 (Table discovery)
- If "Yes": Continue to Phase 4

---

## Phase 4: Confirmation (Lightweight)

**Type:** Lightweight decision

**Header Update:**
```
✓ Schema      ✓ Table       ✓ Preview     ☐ Confirm
```

**Ask for final confirmation:**

```
AskUserQuestion:
  question: "Ready to proceed with `samples.CollibraEmployees`?"
  header: "Confirm"
  multiSelect: false
  options:
    - label: "Yes, proceed (Recommended)"
      description: "Continue to next step"
    - label: "Go back"
      description: "Modify earlier choices"
    - label: "Exit"
      description: "Cancel and finish"
```

**Final header:**

```
═══════════════════════════════════════════════════════════════════════════════
✓ Schema      ✓ Table       ✓ Preview     ✓ Confirm
═══════════════════════════════════════════════════════════════════════════════

DISCOVERY COMPLETE ✓
  Schema: samples
  Table: CollibraEmployees
  Total rows: 2,847
  Columns: 4

Ready for next step (Onboarding/Rules)?
```

---

## Key Implementation Details

### Multi-Section Header Helper

```python
def print_header(phases: list, completed: list):
    """Print multi-section header with progress"""
    header_parts = []
    for phase in phases:
        if phase in completed:
            header_parts.append(f"✓ {phase}")
        else:
            header_parts.append(f"☐ {phase}")

    print("\n" + "="*80)
    print("    ".join(header_parts))
    print("="*80 + "\n")
```

### Skill Execution Pattern

```python
def run_skill_and_display(skill_name: str, args: str):
    """Run a CDQ skill and display raw output"""
    print(f"🔄 [RUNNING SKILL: {skill_name} {args}]\n")
    result = run_skill(skill_name, args=args)
    print(result)
    print()
```

### Validation Loop Pattern

```python
def validation_loop(question, options):
    """Ask question and handle loops"""
    while True:
        response = AskUserQuestion(...)

        if response == "Yes":
            return "confirmed"
        elif response == "Show more":
            # Re-run skill with different limit
            run_skill_and_display(...)
            continue  # Loop again
        elif response == "Choose different":
            return "back"
        else:
            return "exit"
```

---

## Related Workflows

---

## Onboarding Workflow

**Goal:** Register a dataset and run a data quality job

### Workflow Header

```
═══════════════════════════════════════════════════════════════════════════════
☐ Data Source   ☐ Config   ☐ Validation   ☐ Execute
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 1: Data Source Selection (Interactive)

**Type:** Interactive with skill execution (reuse Discovery if already done)

**Header Update:**
```
☐ Data Source   ☐ Config   ☐ Validation   ☐ Execute
```

**Step 1a: Check for Discovery State**

If user completed Discovery workflow:
- Suggest: "Use `{schema}.{table}` from your discovery?"
- If yes: Skip to Phase 2
- If no: Run discovery (same as `/auto-cdq discovery`)

If starting fresh:
- Start mini-discovery flow (Phases 1-3 from Discovery Workflow)

**Step 1b: Display Selected Source**

```
✓ Data Source Selected:
  Schema: samples
  Table: CollibraEmployees
  Total rows: 2,847
```

---

## Phase 2: Dataset Configuration (Lightweight)

**Type:** Lightweight decision with optional custom input

**Header Update:**
```
✓ Data Source   ☐ Config   ☐ Validation   ☐ Execute
```

**Step 2a: Suggest Dataset Name**

Suggest logical name: `{table}_dq`

```
AskUserQuestion:
  question: "What should we call this dataset?"
  header: "Dataset Name"
  multiSelect: false
  options:
    - label: "CollibraEmployees_dq (Recommended)"
      description: "Use suggested name"
    - label: "Type something else"
      description: "Enter a custom dataset name"
    - label: "Chat about this"
      description: "Discuss naming conventions"
```

**Step 2b: Sample Size**

```
AskUserQuestion:
  question: "How many rows should we analyze?"
  header: "Sample Size"
  multiSelect: false
  options:
    - label: "10,000 rows (Recommended)"
      description: "Conservative - quick and safe"
    - label: "50,000 rows"
      description: "Medium - good balance"
    - label: "100,000 rows"
      description: "Large - comprehensive analysis"
    - label: "Full dataset"
      description: "All rows - production onboarding"
    - label: "Type something else"
      description: "Enter specific row count"
```

Store dataset name and row limit.

**Display update:**
```
✓ Data Source   ✓ Config   ☐ Validation   ☐ Execute

DATASET CONFIGURED ✓
  Dataset name: CollibraEmployees_dq
  Row limit: 10,000
```

---

## Phase 3: Validation (Interactive with Skill Execution)

**Type:** Interactive with skill execution and potential loops

**Header Update:**
```
✓ Data Source   ✓ Config   ☐ Validation   ☐ Execute
```

**Step 3a: Test Connection**

```
Run: /cdq-test-connection
```

**Display:**
```
🔄 [RUNNING SKILL: cdq-test-connection]

Connection Status:
✓ Connected to CDQ API
✓ Credentials verified
✓ Ready to proceed
```

**Step 3b: Validate Row Count**

```
Run: /cdq-run-sql --sql "SELECT COUNT(*) as count FROM `samples.CollibraEmployees`"
```

**Display:**
```
🔄 [RUNNING SKILL: cdq-run-sql]

Query:
  SELECT COUNT(*) FROM `samples.CollibraEmployees`

Results:
  Total rows in table: 2,847
  Will onboard: 10,000 (full table, all rows available)
  Processing time estimate: ~30 seconds
```

**Step 3c: Ask for Confirmation**

```
AskUserQuestion:
  question: "Ready to onboard dataset 'CollibraEmployees_dq'?\n\nThis will:\n• Analyze 10,000 rows from samples.CollibraEmployees\n• Register as dataset 'CollibraEmployees_dq'\n• Run initial DQ job"
  header: "Validation"
  multiSelect: false
  options:
    - label: "Yes, proceed (Recommended)"
      description: "Start onboarding"
    - label: "Modify settings"
      description: "Change dataset name or row limit"
    - label: "Chat about this"
      description: "Discuss the configuration"
    - label: "Cancel"
      description: "Exit onboarding"
```

Handle loops:
- If "Modify settings": Go back to Phase 2
- If "Cancel": Exit workflow
- If "Yes": Continue to Phase 4

**Display update:**
```
✓ Data Source   ✓ Config   ✓ Validation   ☐ Execute

VALIDATION PASSED ✓
  Connection: Working
  Row count: 2,847 available
  Status: Ready to execute
```

---

## Phase 4: Execute & Results (Interactive with Skill Execution)

**Type:** Skill execution with progress and results display

**Header Update:**
```
✓ Data Source   ✓ Config   ✓ Validation   ☐ Execute
```

**Step 4a: Run Onboarding Job**

```
Run: /cdq-run-dq-job --dataset "CollibraEmployees_dq" --sql "SELECT * FROM `samples.CollibraEmployees` LIMIT 10000"
```

**Display:**
```
🔄 [RUNNING SKILL: cdq-run-dq-job]

Starting DQ job for dataset 'CollibraEmployees_dq'...
  • Registering dataset
  • Analyzing 10,000 rows
  • Processing...

✓ Job complete!
  Job ID: job_20250409_001
  Status: SUCCESS
  Duration: 32 seconds
```

**Step 4b: Retrieve Results**

```
Run: /cdq-get-results --dataset "CollibraEmployees_dq"
```

**Display:**
```
🔄 [RUNNING SKILL: cdq-get-results]

DQ Score: 87.3%

Summary:
  • Rows analyzed: 10,000
  • Rows passed: 8,730
  • Rows flagged: 1,270

Quality Breakdown:
  • Completeness: 92%
  • Uniqueness: 85%
  • Validity: 81%
```

**Step 4c: Final Confirmation**

```
═══════════════════════════════════════════════════════════════════════════════
✓ Data Source   ✓ Config   ✓ Validation   ✓ Execute
═══════════════════════════════════════════════════════════════════════════════

🎉 ONBOARDING COMPLETE

Dataset: CollibraEmployees_dq
Status: Active ✓
Quality Score: 87.3%

Next Steps:
  → Create rules to fix quality issues
  → Set up alerts for monitoring
  → Schedule recurring DQ jobs
```

**Ask for next action:**

```
AskUserQuestion:
  question: "Onboarding complete! What would you like to do next?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Create rules (Recommended)"
      description: "Build rules to catch quality issues"
    - label: "Set up alerts"
      description: "Configure alerts for violations"
    - label: "Run workflow again"
      description: "Onboard another dataset"
    - label: "Exit"
      description: "Finish for now"
```

---

---

## Rules Workflow

**Goal:** Analyze data and create quality rules

### Workflow Header

```
═══════════════════════════════════════════════════════════════════════════════
☐ Dataset    ☐ Analysis    ☐ Select    ☐ Test & Save
═══════════════════════════════════════════════════════════════════════════════
```

---

## Phase 1: Dataset Selection (Lightweight/Interactive)

**Type:** Lightweight question or mini-discovery

**Header Update:**
```
☐ Dataset    ☐ Analysis    ☐ Select    ☐ Test & Save
```

**Option A: Reuse Onboarding Dataset**

If user just completed onboarding:
```
Suggest: "Use 'CollibraEmployees_dq' from your onboarding?"
If yes: Skip to Phase 2
If no: Continue to Option B
```

**Option B: Select or Search Dataset**

```
AskUserQuestion:
  question: "Which dataset should we create rules for?"
  header: "Dataset"
  multiSelect: false
  options:
    - label: "CollibraEmployees_dq (Recommended)"
      description: "From your recent onboarding"
    - label: "Search catalog"
      description: "Find a dataset in Collibra"
    - label: "Type something else"
      description: "Enter dataset name"
    - label: "Chat about this"
      description: "Discuss datasets"
```

Store selected dataset.

**Display update:**
```
✓ Dataset    ☐ Analysis    ☐ Select    ☐ Test & Save

DATASET SELECTED ✓
  Dataset: CollibraEmployees_dq
  Quality score: 87.3%
```

---

## Phase 2: Data Analysis (Interactive with Skill Execution)

**Type:** Interactive with skill execution

**Header Update:**
```
✓ Dataset    ☐ Analysis    ☐ Select    ☐ Test & Save
```

**Step 2a: Run Analysis**

```
Run: /cdq-workflow-suggest-rules --dataset "CollibraEmployees_dq"
```

**Display:**
```
🔄 [RUNNING SKILL: cdq-workflow-suggest-rules]

Analyzing dataset 'CollibraEmployees_dq'...

Found 12 rule opportunities:

┌─────────┬────────────────────────────────────┬───────────┬──────────────┐
│ Priority│ Rule Name                          │ Type      │ Impact       │
├─────────┼────────────────────────────────────┼───────────┼──────────────┤
│ HIGH    │ id_not_null                        │ Complete  │ 0 violations │
│ HIGH    │ name_not_null                      │ Complete  │ 12 violations│
│ HIGH    │ id_uniqueness                      │ Unique    │ 0 violations │
│ MEDIUM  │ department_allowed_values          │ Validity  │ 3 violations │
│ MEDIUM  │ start_date_format                  │ Format    │ 5 violations │
│ MEDIUM  │ start_date_not_future              │ Range     │ 0 violations │
│ LOW     │ name_length_check                  │ Custom    │ 2 violations │
│ LOW     │ department_distribution_monitor    │ Custom    │ N/A          │
└─────────┴────────────────────────────────────┴───────────┴──────────────┘

Recommendations:
  • 4 HIGH priority rules (critical issues)
  • 3 MEDIUM priority rules (data quality improvements)
  • 5 LOW priority rules (monitoring/trends)

All rules have been tested against the dataset.
```

**Display update:**
```
✓ Dataset    ✓ Analysis    ☐ Select    ☐ Test & Save

ANALYSIS COMPLETE ✓
  Rules found: 12 (4 HIGH, 3 MEDIUM, 5 LOW)
  Status: Ready for selection
```

---

## Phase 3: Rule Selection (Lightweight)

**Type:** Lightweight multi-select decision

**Header Update:**
```
✓ Dataset    ✓ Analysis    ☐ Select    ☐ Test & Save
```

**Step 3a: Select Rules**

```
AskUserQuestion:
  question: "Which rules should we create?\n\n[Grouped by priority]"
  header: "Rule Selection"
  multiSelect: true
  options:
    - label: "[HIGH] name_not_null - 12 violations (Recommended)"
      description: "Completeness check - catch missing names"
    - label: "[HIGH] id_uniqueness - 0 violations (Recommended)"
      description: "Uniqueness check - ensure IDs are unique"
    - label: "[HIGH] department_allowed_values"
      description: "Validity check - only valid departments"
    - label: "[MEDIUM] start_date_format - 5 violations"
      description: "Format check - dates must be valid"
    - label: "[MEDIUM] start_date_not_future"
      description: "Range check - dates cannot be in future"
    - label: "[LOW] name_length_check"
      description: "Custom check - reasonable name lengths"
    - label: "Select all HIGH priority (Recommended)"
      description: "Create all 4 high-priority rules"
    - label: "Chat about this"
      description: "Discuss rule options"
```

Store selected rules.

**Display update:**
```
✓ Dataset    ✓ Analysis    ✓ Select    ☐ Test & Save

RULES SELECTED ✓
  Selected: 4 rules
    • 3 HIGH priority
    • 1 MEDIUM priority
```

---

## Phase 4: Test & Save (Interactive with Validation Loop & Batch Execution)

**Type:** Complex batch operation with per-item validation

**Header Update:**
```
✓ Dataset    ✓ Analysis    ✓ Select    ☐ Test & Save
```

**Step 4a: Test Each Rule**

For EACH selected rule:

```
Running rule: name_not_null (1 of 4)
Query: SELECT * FROM samples.CollibraEmployees WHERE name IS NULL

🔄 [RUNNING SKILL: cdq-run-sql]

Results:
  • Rows violating rule: 12
  • Pass rate: 99.9%
  • Sample violations:
    Row 42: name=NULL, id=E042, department=Engineering
    Row 178: name=NULL, id=E178, department=Sales
```

**Display all tested rules summary:**
```
Rule Testing Complete (4 of 4):

✓ name_not_null - 12 violations flagged
✓ id_uniqueness - 0 violations (passed)
✓ department_allowed_values - 3 violations flagged
✓ start_date_format - 5 violations flagged

Ready to save these rules?
```

**Step 4b: Ask for Batch Confirmation**

```
AskUserQuestion:
  question: "All 4 rules tested successfully.\n\nReady to save to dataset 'CollibraEmployees_dq'?"
  header: "Confirm & Save"
  multiSelect: false
  options:
    - label: "Yes, save all rules (Recommended)"
      description: "Create all 4 rules in dataset"
    - label: "Save with modifications"
      description: "Adjust rule SQL before saving"
    - label: "Select different rules"
      description: "Go back to Phase 3"
    - label: "Cancel"
      description: "Don't save rules"
```

**Step 4c: Save Rules Batch**

For EACH approved rule:
```
Run: /cdq-save-rule --dataset "CollibraEmployees_dq" --name "{rule_name}" --sql "{rule_sql}"
```

**Display:**
```
🔄 [RUNNING SKILL: cdq-save-rule]

Saving rules to dataset 'CollibraEmployees_dq'...

✓ Rule 1/4: name_not_null (saved)
✓ Rule 2/4: id_uniqueness (saved)
✓ Rule 3/4: department_allowed_values (saved)
✓ Rule 4/4: start_date_format (saved)

All rules saved successfully!
```

**Final Display:**

```
═══════════════════════════════════════════════════════════════════════════════
✓ Dataset    ✓ Analysis    ✓ Select    ✓ Test & Save
═══════════════════════════════════════════════════════════════════════════════

🎉 RULES CREATED SUCCESSFULLY

Dataset: CollibraEmployees_dq
Status: 4 rules now active

Rules:
  1. name_not_null (HIGH) - 12 violations
  2. id_uniqueness (HIGH) - 0 violations
  3. department_allowed_values (HIGH) - 3 violations
  4. start_date_format (MEDIUM) - 5 violations

Next Steps:
  → Run DQ job to validate rules against full data
  → Create alerts for rule violations
  → Set up monitoring dashboard
```

**Ask for next action:**

```
AskUserQuestion:
  question: "Rules created! What's next?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Run DQ job (Recommended)"
      description: "Execute job with new rules"
    - label: "Create alerts"
      description: "Set up notifications"
    - label: "Create more rules"
      description: "Add additional rules"
    - label: "Exit"
      description: "Finish for now"
```

---

All follow the same hybrid pattern with multi-section headers and skill execution.

See `docs/HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md` for full pattern reference.
