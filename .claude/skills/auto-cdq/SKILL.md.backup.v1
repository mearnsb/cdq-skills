---
name: auto-cdq
description: Enhanced guided CDQ workflow assistant with autoresearch-style wizard experience featuring numbered menus, dynamic suggestions, and multi-phase workflows.
commands:
  - name: auto-cdq
    description: Show workflow selection menu (Discovery, Onboarding, Rules)
  - name: auto-cdq:discovery
    description: Jump straight to Discovery Workflow - find and preview tables
  - name: auto-cdq:onboarding
    description: Jump straight to Onboarding Workflow - register dataset and run DQ job
  - name: auto-cdq:rules
    description: Jump straight to Rules Workflow - analyze data and create quality rules
---

# Auto-CDQ — Interactive Wizard

An interactive, autoresearch-style wizard for Collibra DQ workflows. When invoked, you become a guided assistant that walks users through schema selection, table discovery, onboarding, and rule creation.

## Core Behavior

### Always Use AskUserQuestion
Present EVERY user choice as numbered options using the AskUserQuestion tool:
- Use `multiSelect: false` for single choices, `true` for multiple selections
- Include 2-6 options per question
- Mark recommended options with "(Recommended)" in the label
- Always include escape hatches like "Type something else" or "Skip"

### Batch Questions
Group related questions into single AskUserQuestion calls (max 4 per batch).

### Use Backend for Data
Use the existing CDQ skills to fetch real data:
- `cdq-search-catalog` — Search for datasets
- `cdq-list-tables --schema X --search Y --limit N` — List tables in a schema
- `cdq-run-sql --sql "SELECT * FROM schema.table LIMIT 5"` — Preview data
- `cdq-run-dq-job --dataset X --sql Y` — Run onboarding job
- `cdq-save-rule --dataset X --name Y --sql Z` — Save a rule
- `cdq-get-rules --dataset X` — Get existing rules
- `cdq-workflow-suggest-rules` — Analyze columns for rule suggestions
- `cdq-test-connection` — Test API connectivity

### Track State
Store progress in `.auto-cdq-state.json` between turns.

---

## Entry Point

When `/auto-cdq` is invoked:

**Step 1:** Check if user specified a workflow in the command:
- `/auto-cdq discovery` → jump to Discovery Workflow
- `/auto-cdq onboarding` → jump to Onboarding Workflow
- `/auto-cdq rules` → jump to Rules Workflow
- No argument → present workflow selection menu

**Step 2:** If no workflow specified, present:

```
AskUserQuestion:
  question: "What would you like to do?"
  header: "Workflow"
  multiSelect: false
  options:
    - label: "Discovery (Recommended)"
      description: "Find and preview tables with guided search"
    - label: "Onboarding"
      description: "Register a dataset and run a DQ job"
    - label: "Rules"
      description: "Analyze data and create quality rules"
    - label: "Exit"
      description: "Finish the session"
```

**Step 3:** Route to the selected workflow.

---

## Discovery Workflow

### Phase 1: Schema Selection

**1.1** Get the configured schema from the project's `.env` file (DQ_SCHEMA).

**1.2** Present schema menu:

```
AskUserQuestion:
  question: "Which schema should we search in?"
  header: "Schema"
  multiSelect: false
  options:
    - label: "{DQ_SCHEMA} (Recommended)"
      description: "Use the schema from your .env configuration"
      (only if DQ_SCHEMA exists)
    - label: "samples"
      description: "Demo/sample schema"
    - label: "Type something else"
      description: "Enter a custom schema name"
    - label: "Chat about this"
      description: "Discuss schema options"
```

**1.3** Handle the answer:
- If "Type something else" → user provides custom schema name
- Otherwise → store selected schema, proceed to Phase 2

### Phase 2: Table Selection

**2.1** Present table menu:

```
AskUserQuestion:
  question: "Which table would you like to work with?"
  header: "Table"
  multiSelect: false
  options:
    - label: "customers (Recommended)"
      description: "Common table: customers"
    - label: "Search by pattern"
      description: "Search tables by name pattern (e.g., %cust%)"
    - label: "Browse all tables"
      description: "List all tables in schema"
    - label: "Type something else"
      description: "Enter a custom table name"
    - label: "Chat about this"
      description: "Discuss table options"
```

**2.2** Handle the answer:

If specific table (customers/claims/nyse):
- Store table name
- Proceed to Phase 3 (Preview)

If "Search by pattern":
- Ask: "Enter a pattern to search for (SQL LIKE syntax):"
- Then run: `cdq-list-tables --schema {schema} --search {pattern} --limit 20`
- Show results as numbered options

If "Browse all tables":
- Run: `cdq-list-tables --schema {schema} --limit 20`
- Show results as numbered options

If custom text input (user types table name):
- Store table name as custom input
- Proceed to Phase 3 (Preview)

### Phase 3: Preview

**3.1** Run preview:
```bash
cdq-run-sql --sql "SELECT * FROM `{schema}.{table}` LIMIT 5"
```

**3.2** Extract and display:
- Column names (from result headers)
- Row count returned
- Sample values (first 3 rows)

**3.3** Present confirmation menu:

```
AskUserQuestion:
  question: "Preview of `{schema}.{table}` (5 rows shown):\n\nColumns: {col1}, {col2}, ...\n\nWhat would you like to do next?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Use this table (Recommended)"
      description: "Proceed with this table"
    - label: "Preview more rows"
      description: "Show additional sample data (LIMIT 20)"
    - label: "Choose different table"
      description: "Go back to table selection"
    - label: "Chat about this"
      description: "Discuss the preview or data"
    - label: "Exit"
      description: "Finish the session"
```

**3.4** Handle answer:
- "Use this table" → proceed to Post-Discovery Menu
- "Preview more rows" → re-run preview with LIMIT 20, show results
- "Choose different table" → return to Phase 2
- "Exit" → clear state, end session

### Phase 4: Post-Discovery Menu

```
AskUserQuestion:
  question: "Found {count} tables in `{schema}`.\n\nTop matches: {table1}, {table2}...\n\nWhat would you like to do next?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Preview a table (Recommended)"
      description: "View sample data from a table"
    - label: "Start onboarding"
      description: "Register a dataset"
    - label: "Refine search"
      description: "Try a different search pattern"
    - label: "Chat about this"
      description: "Discuss the results"
    - label: "Exit"
      description: "Finish the session"
```

---

## Onboarding Workflow

### Phase 1: Table Selection
Same as Discovery Phases 1-3. User must select a table first.

### Phase 2: Dataset Configuration

**2.1** Suggest dataset name: `{table}_dq`

**2.2** Present configuration (batch 1 of 2):

```
AskUserQuestion:
  question: "Configure onboarding for `{schema}.{table}`:"
  header: "Dataset Name"
  multiSelect: false
  options:
    - label: "{table}_dq (Recommended)"
      description: "Use suggested name"
    - label: "Type something else"
      description: "Enter a different dataset name"
    - label: "Chat about this"
      description: "Discuss naming conventions"
```

**2.3** Present sample size (batch 2 of 2):

```
AskUserQuestion:
  question: "How many rows should we onboard?"
  header: "Sample Size"
  multiSelect: false
  options:
    - label: "10,000 rows (Recommended)"
      description: "Conservative sample - fast and safe"
    - label: "50,000 rows"
      description: "Medium sample - good balance"
    - label: "100,000 rows"
      description: "Large sample - more comprehensive"
    - label: "Type something else"
      description: "Enter a specific row count"
    - label: "Chat about this"
      description: "Discuss sample size options"
```

### Phase 3: Validation

**3.1** Build test query:
```sql
SELECT * FROM `{schema}.{table}` LIMIT 10
```

**3.2** Run validation:
```bash
cdq-run-sql --sql "SELECT * FROM `{schema}.{table}` LIMIT 10"
```

**3.3** If validation fails:
- Show error message
- Offer to: modify table name, choose different table, or exit

**3.4** If validation passes:
- Show row count that will be onboarded
- Ask for final confirmation:

```
AskUserQuestion:
  question: "Validation passed. This will onboard {count} rows to dataset '{dataset}'.\n\nProceed with onboarding?"
  header: "Confirm"
  multiSelect: false
  options:
    - label: "Yes, proceed (Recommended)"
      description: "Start the onboarding job"
    - label: "Modify settings"
      description: "Change dataset name or limit"
    - label: "Chat about this"
      description: "Discuss onboarding options"
    - label: "Cancel"
      description: "Return to menu"
```

### Phase 4: Execution

**4.1** Run onboarding job:
```bash
cdq-run-dq-job --dataset {dataset} --sql "SELECT * FROM `{schema}.{table}` LIMIT {limit}"
```

**4.2** Show result:
- Dataset name
- Job status
- Run ID

### Phase 5: Post-Onboarding

```
AskUserQuestion:
  question: "Onboarding job started for dataset '{dataset}'.\n\nWhat would you like to do next?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Check job status (Recommended)"
      description: "Monitor the onboarding job"
    - label: "Create rules"
      description: "Go to rules wizard"
    - label: "Chat about this"
      description: "Discuss next steps"
    - label: "Exit"
      description: "Finish the session"
```

---

## Rules Workflow

### Phase 1: Table Selection
Same as Discovery Phases 1-3. User must select a table first.

### Phase 2: Column Analysis

**2.1** Run analysis:
```bash
cdq-workflow-suggest-rules
```
(This skill will analyze the selected table's columns and suggest rules)

**2.2** Parse suggestions from result. Each suggestion contains:
- `column`: column name
- `type`: completeness, uniqueness, validity, range
- `priority`: high, medium, low
- `description`: human-readable description
- `suggested_rule`: SQL for the rule

### Phase 3: Rule Selection

**3.1** Group by priority:
- HIGH priority first
- MEDIUM priority second
- LOW priority last

**3.2** Present selection menu:

```
AskUserQuestion:
  question: "Found {count} potential data quality rules.\n\nHigh priority: {high_count} | Medium priority: {med_count}\n\nSelect rules to create:"
  header: "Rules"
  multiSelect: true
  options:
    - label: "[HIGH] {type}: {column} (Recommended)"
      description: "{description}"
      (for each high-priority suggestion, max 5)
    - label: "[MED] {type}: {column}"
      description: "{description}"
      (for each medium-priority suggestion, max 5)
    - label: "Select all suggestions"
      description: "Create all recommended rules"
    - label: "Type something else"
      description: "Create a custom rule"
    - label: "Chat about this"
      description: "Discuss rule options"
    - label: "Skip rules"
      description: "Exit without creating rules"
```

### Phase 4: Rule Testing

For EACH selected rule:

**4.1** Show rule details:
```
Rule: {rule_name}
Type: {rule_type}
SQL: {rule_sql}
```

**4.2** Test the SQL by running:
```bash
cdq-run-sql --sql "{rule_sql}"
```

**4.3** Show flagged row count.

**4.4** Ask for confirmation:

```
AskUserQuestion:
  question: "Rule: {rule_name}\n\nSQL: {rule_sql}\n\nWould flag {count} rows if applied.\n\nWhat would you like to do?"
  header: "Confirm Rule"
  multiSelect: false
  options:
    - label: "Save this rule (Recommended)"
      description: "Add to dataset"
    - label: "Modify rule"
      description: "Adjust the SQL"
    - label: "Chat about this"
      description: "Discuss the rule"
    - label: "Skip this rule"
      description: "Don't create this rule"
```

### Phase 5: Save Rules

**5.1** For each approved rule:
```bash
cdq-save-rule --dataset {dataset} --name "{rule_name}" --sql "{rule_sql}"
```

**5.2** Show summary:
```
Saved {N} rules to dataset '{dataset}':
  1. {rule_name_1} - {type}
  2. {rule_name_2} - {type}
  ...
```

### Phase 6: Post-Rules

```
AskUserQuestion:
  question: "Created {N} rules for '{dataset}'.\n\nWhat would you like to do next?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Run DQ job (Recommended)"
      description: "Execute job with new rules"
    - label: "Create more rules"
      description: "Return to rule selection"
    - label: "Chat about this"
      description: "Discuss the rules created"
    - label: "Exit"
      description: "Finish the session"
```

---

## Error Handling

### Connection Failure
If any backend command fails with connection error:

1. Run `cdq-test-connection`

2. Show error clearly:
```
Connection test failed.
Error: {error_message}

Remediation:
1. Check your .env file for DQ_URL, DQ_USER, DQ_PASSWORD
2. Verify network connectivity to CDQ server
```

3. Offer to: retry, continue with cached data, or exit

### No Results Found
If list-tables returns 0 tables:

```
AskUserQuestion:
  question: "Found 0 tables in `{schema}` matching \"{search}\".\n\nWhat would you like to do?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Refine search (Recommended)"
      description: "Try a different search pattern"
    - label: "Choose different schema"
      description: "Select another schema"
    - label: "Chat about this"
      description: "Discuss search strategy"
    - label: "Exit"
      description: "Finish the session"
```

### Invalid SQL
If run-sql fails:

```
AskUserQuestion:
  question: "SQL validation failed.\n\nQuery: {sql}\nError: {error_message}\n\nWhat would you like to do?"
  header: "Next Step"
  multiSelect: false
  options:
    - label: "Modify query"
      description: "Adjust the SQL"
    - label: "Use different table"
      description: "Select another table"
    - label: "Chat about this"
      description: "Discuss the error"
    - label: "Exit"
      description: "Finish the session"
```

---

## State File Format

Store state in `.auto-cdq-state.json`:

```json
{
  "phase": "discovery_schema",
  "workflow": "discovery",
  "schema": "DQ_SCHEMA",
  "table": null,
  "dataset": null,
  "limit": 10000,
  "selected_rules": [],
  "available_schemas": ["DQ_SCHEMA", "samples"],
  "preview_data": null,
  "analysis_result": null
}
```

**State lifecycle:**
- Load at start of each turn
- Update after each user answer
- Clear on "Exit" or error
- Persist across session restarts

---

## Quick Reference: Option Labels

Use these exact patterns for consistency:

**Workflow:**
- "Discovery (Recommended)"
- "Onboarding"
- "Rules"
- "Exit"

**Schema:**
- "{schema} (Recommended)"
- "samples"
- "Type something else" (for custom schema)
- "Chat about this"

**Table:**
- "customers (Recommended)"
- "Search by pattern"
- "Browse all tables"
- (CLI auto-provides text input for custom table names)

**Next Steps:**
- "{action} (Recommended)"
- "Refine search"
- "Choose different {type}"
- "Exit"

**Rules:**
- "[HIGH] {Type}: {column} (Recommended)"
- "[MED] {Type}: {column}"
- "[LOW] {Type}: {column}"
- "Select all suggestions"
- "Create custom rule"
- "Skip rules"

---

## Testing Checklist

Before considering this skill complete, verify:

- [ ] Workflow menu appears first
- [ ] Schema menu shows configured schema as recommended
- [ ] "Fetch from catalog" returns actual schemas
- [ ] Table menu shows common suggestions
- [ ] "Search by pattern" filters tables correctly
- [ ] Preview shows rows with column names
- [ ] Post-discovery menu offers onboarding
- [ ] Onboarding suggests correct dataset name
- [ ] Sample size options appear
- [ ] SQL validation runs before job
- [ ] Rules analysis detects NULL patterns
- [ ] High priority rules shown first
- [ ] Rule SQL test shows flagged count
- [ ] State persists across answers
- [ ] State clears on Exit
- [ ] Error handling shows helpful messages
