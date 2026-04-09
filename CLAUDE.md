# CDQ Skills Project Context

This project contains Collibra DQ (Data Quality) skills for Claude Code. These skills provide direct REST API access to CDQ without MCP dependencies.

## Key Environment
- Preferred model: `minimax/minimax-m2.5`
- Settings file: `.claude/settings.local.json`

## Available Skills (Invoke with /skill-name)
- auto-cdq - Enhanced guided CDQ workflow assistant with wizard experience
- cdq-get-alerts - Retrieve alerts for a dataset
- cdq-get-dataset - Get dataset configuration
- cdq-get-jobs - List queued/running DQ jobs
- cdq-get-recent-runs - Get recent job run IDs/timestamps
- cdq-get-results - Retrieve DQ job results
- cdq-get-rules - Retrieve DQ rules for a dataset
- cdq-list-tables - List physical tables in database
- cdq-run-dq-job - Register and run DQ jobs
- cdq-run-sql - Execute SQL queries directly
- cdq-save-alert - Create new alerts
- cdq-save-rule - Create new DQ rules
- cdq-search-catalog - Search registered datasets
- cdq-test-connection - Test API connection
- cdq-workflow-* - Complete workflows
- fake-data-generator - Generate test data

## CDQ Concepts
- Connection: JDBC/cloud storage access (BIGQUERY, SNOWFLAKE, etc.)
- Dataset: Logical name (NOT schema.table) - rules/alerts attach here
- Rule: SQL query that identifies problem records
- Job: Execution of a dataset with all rules
- Results: Scores and findings from job execution

## Safety Limits (Always Apply These)
- Use LIMIT clauses in SQL queries (default: 100,000)
- For exploration: LIMIT 5 or LIMIT 1000
- For onboarding: LIMIT 10000-50000
- For large tables: Add date filters or sample data

## Standard Workflow Patterns
1. Explore → Preview → Onboard → Validate
2. Analyze → Propose → Test → Save Rules
3. Batch Processing with Checkpoint Validation

See EXAMPLE_PROMPTS.md for detailed multi-step workflow templates.

## Error Handling Guidelines
- Always test SQL queries with cdq-run-sql before using in rules
- Check job results with cdq-get-results to validate success
- Handle authentication errors with cdq-test-connection
- Use LIMIT to prevent runaway queries

## Key Distinctions
- Use cdq-run-sql with actual schema.table names
- Use cdq-save-rule, cdq-get-rules with dataset names (logical)
- Rules and Alerts attach to datasets, not database tables

## Gemini CLI Usage

**Recommended command:**
```bash
~/.claude/bin/gemini-search -p "your query" [--approval-mode yolo]
```

Create an alias for convenience:
```bash
echo "alias gsearch='~/.claude/bin/gemini-search'" >> ~/.zshrc
```

Then use: `gsearch -p "your query"`

**Note:** The old `gemini-wrapper.sh` has been deprecated (`.gemini-wrapper.sh.deprecated`). Use `gemini-search` instead — it's simpler, more reliable, and covers all use cases.

For system-wide Gemini access from any project, use: `/gemini` skill

---

## Sequential Thinking Integration
For complex tasks, use this pattern:

```
Use sequential-thinking to plan, analyze, and validate the following task:

### Phase 1: Discovery & Exploration
**Step 1.1:** Find relevant tables/datasets using cdq-search-catalog or cdq-list-tables
**Step 1.2:** Preview data with cdq-run-sql using LIMIT 5 for safety

### Phase 2: Execution & Onboarding
**Step 2.1:** Register dataset with cdq-run-dq-job using appropriate LIMIT
**Step 2.2:** Validate job completion with cdq-get-results

### Phase 3: Rule Generation & Analysis
**Step 3.1:** Analyze data patterns for rule opportunities
**Step 3.2:** Test rule logic with cdq-run-sql before saving
**Step 3.3:** Save validated rules with cdq-save-rule

### Success Criteria
✅ All discovery steps completed successfully
✅ Dataset registered and validated
✅ Rules tested and saved appropriately
```