# Example Prompts for Multi-Step CDQ Workflows

This document provides structured prompt templates for complex, multi-step CDQ tasks. These prompts are designed to work with **sequential-thinking** for planning, validation, and progress tracking.

## Prerequisites

### Enable Sequential Thinking

Sequential thinking is available as an MCP server and helps break down complex tasks into verifiable steps with tracking checkpoints.

**Option 1: NPX Quick Start (Recommended)**
```bash
npx mcp-server-sequential-thinking
```

**Option 2: Use Anthropic Reference Server**
- Repository: [anthropic-ai/mcp-servers](https://github.com/anthropic-ai/mcp-servers)
- Server: `sequential-thinking` directory
- Full docs: Follow the Anthropic MCP setup instructions

**In Claude Code:**
```bash
# Enable sequential-thinking in your project via MCP settings
# or use it globally by adding to your Claude Code config
```

### Why Sequential Thinking?

For multi-step CDQ tasks (especially those with discovery, onboarding, validation, and rule generation), sequential-thinking provides:
- **Checkpoints**: Track progress at each step
- **Validation**: Verify assumptions before proceeding
- **Atomicity**: Mark step completion/failure clearly
- **Context preservation**: Maintain state across multiple operations
- **Debugging**: Easy to identify which step failed

---

## Example Prompt 1: Automated Employee Table Discovery, Onboarding & DQ Rule Generation

**Use case:** Discover all tables containing "employee" in the name, onboard them as datasets, and generate domain-specific data quality rules.

### Prompt Text

```
Use sequential-thinking to plan, analyze, and validate the following task:

## Task: Automated Employee Table Discovery, Onboarding & Data Quality Rule Generation

### Phase 1: Discovery & Preview
**Step 1.1: Find Employee Tables**
- Use cdq-list-tables or cdq-run-sql to search for tables with "employee" in the name
- Use SQL: `SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%employee%'`
- Use sequential-thinking to document all matching table names

**Step 1.2: Preview Each Table**
- For each discovered table, run: `SELECT * FROM <table_name> LIMIT 5`
- Use cdq-run-sql for these queries (use actual schema.table names)
- Document schema: column names, data types, nullable fields
- Track data characteristics (patterns, ranges, domain logic)

### Phase 2: Dataset Onboarding
**Step 2.1: Prepare Onboarding** (per table)
- Dataset name format: `AI_AUTO_ONBOARDED_<table_name>`
- SQL query: `SELECT * FROM <table_name> LIMIT 10000`
- Log configuration for checkpoint

**Step 2.2: Execute Onboarding Jobs** (per table)
- Use cdq-run-dq-job to onboard each dataset
- Capture job IDs and timestamps
- Track in sequential-thinking

**Step 2.3: Validate Onboarding Success**
- Use cdq-get-results to check job completion
- Verify dataset ingestion (row count matches expected)
- Use sequential-thinking to validate each milestone
- Flag any failures for remediation

### Phase 3: Data Quality Rules Generation
**Step 3.1: Analyze Data for Rule Design** (per table)
- Review column types and distributions
- Identify data domain (employee records → dates, emails, salary ranges)
- Use sequential-thinking to plan 5-10 domain-specific rules

**Step 3.2: Generate Rule Suggestions** (domain-specific categories)
Examples:
- **Completeness**: NOT NULL on critical fields (employee_id, email, hire_date)
- **Uniqueness**: employee_id must be unique
- **Format**: Email pattern, phone format, SSN format
- **Range**: Salary within bounds, hire_date not in future, age 18-120
- **Referential**: Foreign keys to department/manager IDs
- **Consistency**: start_date < end_date (if present)
- **Domain Logic**: Status codes in (ACTIVE, INACTIVE, LEAVE), department codes valid

**Step 3.3: Test Each Rule**
- Use cdq-run-sql to validate rule syntax with: `SELECT COUNT(*) FROM <table_name> WHERE <rule_condition>`
- Example: `SELECT COUNT(*) FROM employees WHERE email NOT LIKE '%@%'`
- Record pass/fail results

**Step 3.4: Save Rules**
- Use cdq-save-rule for each validated rule
- Associate with dataset: `AI_AUTO_ONBOARDED_<table_name>`
- Document rule name, description, SQL logic

### Phase 4: Completion & Validation
**Step 4.1: Generate Summary Report**
- Total tables discovered: ___
- Tables successfully onboarded: ___
- Total rules created and saved: ___
- Any failures or manual review needed: ___

**Step 4.2: Use Sequential-Thinking Final Validation**
- Confirm all steps completed in sequence
- Verify discovered tables vs. onboarded datasets
- Verify rule count per table (should be 5-10)
- Flag any gaps

---

## Execution Guidelines

1. **Use sequential-thinking BETWEEN major phases** to validate progress
2. **Use cdq-* skills** for all Collibra operations:
   - Discovery: cdq-run-sql, cdq-list-tables
   - Onboarding: cdq-run-dq-job
   - Rules: cdq-save-rule, cdq-run-sql (for testing)
   - Validation: cdq-get-results, cdq-get-rules
3. **Track metrics throughout**: tables found → onboarded → rules created
4. **Test before saving**: Always validate with SQL queries
5. **Document failures**: Note tables/rules that fail
6. **Atomic operations**: Complete each table fully before next

---

## Success Criteria

✅ All "employee" tables discovered and documented
✅ Each table onboarded with `AI_AUTO_ONBOARDED_*` naming
✅ Onboarding jobs validated as complete
✅ 5-10 domain-specific rules per table
✅ All rules tested and saved
✅ Complete audit trail via sequential-thinking checkpoints
```

### How to Use

1. Copy the prompt text above
2. Paste into Claude Code or your AI assistant
3. Enable sequential-thinking MCP server
4. Invoke cdq-* skills as directed
5. Let sequential-thinking track progress through all phases

---

## Example Prompt 1B: Automated Loan/Customer Table Discovery, Onboarding & DQ Rule Generation

**Use case:** Discover all tables containing "loan" or "customer" in the name, onboard them as datasets, and generate domain-specific data quality rules for loan/credit data.

### Prompt Text

```
Use sequential-thinking to plan, analyze, and validate the following task:

## Task: Automated Loan/Customer Table Discovery, Onboarding & Data Quality Rule Generation

### Phase 1: Discovery & Preview
**Step 1.1: Find Loan/Customer Tables**
- Use cdq-list-tables or cdq-run-sql to search for tables with "loan" or "customer" in the name
- Use SQL: `SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%loan%' OR TABLE_NAME LIKE '%customer%'`
- Use sequential-thinking to document all matching table names

**Step 1.2: Preview Each Table**
- For each discovered table, run: `SELECT * FROM <schema.table_name> LIMIT 5`
- Use cdq-run-sql for these queries (use actual schema.table names - e.g., samples.loan_customer)
- Document schema: column names, data types, nullable fields
- Track data characteristics (patterns, ranges, domain logic)
- Get full column list: `SELECT STRING_AGG(column_name, ', ') FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '<table_name>'`

### Phase 2: Dataset Onboarding
**Step 2.1: Prepare Onboarding** (per table)
- Dataset name format: `AI_AUTO_ONBOARDED_<table_name>`
- SQL query: `SELECT * FROM <schema.table_name> LIMIT 10000`
- Log configuration for checkpoint

**Step 2.2: Execute Onboarding Jobs** (per table)
- Use cdq-run-dq-job to onboard each dataset
- Capture job IDs and timestamps
- Track in sequential-thinking

**Step 2.3: Validate Onboarding Success**
- Use cdq-get-results to check job completion
- Verify dataset ingestion (row count matches expected)
- Use sequential-thinking to validate each milestone
- Flag any failures for remediation

### Phase 3: Data Quality Rules Generation
**Step 3.1: Analyze Data for Rule Design** (per table)
- Review column types and distributions
- Identify data domain (loan/credit records → SSN, rates, balances, VINs)
- Use sequential-thinking to plan 5-10 domain-specific rules

**Step 3.2: Generate Rule Suggestions** (domain-specific categories)
Examples for loan/customer data:
- **Completeness**: NOT NULL on critical fields (ssn_number, email, loan_id)
- **Uniqueness**: SSN must be unique
- **Format**: Email pattern (regex), phone format, SSN format, car VIN (17 chars)
- **Range**: loan_rate 0-100%, personal loan rate 0-100%, mortgage balance >= 0
- **Consistency**: months_behind >= 0, payments_remaining >= 0
- **Domain Logic**: loan types in (bankcard, mortgage, auto, personal), valid currency codes

**Step 3.3: Test Each Rule**
- Use cdq-run-sql to validate rule syntax with: `SELECT COUNT(*) FROM <table_name> WHERE <rule_condition>`
- Example: `SELECT COUNT(*) FROM samples.loan_customer WHERE loan_rate < 0 OR loan_rate > 100`
- Record pass/fail results

**Step 3.4: Save Rules**
- Use cdq-save-rule for each validated rule
- Associate with dataset: `AI_AUTO_ONBOARDED_<table_name>`
- Document rule name, description, SQL logic

### Phase 4: Completion & Validation
**Step 4.1: Generate Summary Report**
- Total tables discovered: ___
- Tables successfully onboarded: ___
- Total rules created and saved: ___
- Any failures or manual review needed: ___

**Step 4.2: Use Sequential-Thinking Final Validation**
- Confirm all steps completed in sequence
- Verify discovered tables vs. onboarded datasets
- Verify rule count per table (should be 5-10)
- Flag any gaps

---

## Execution Guidelines

1. **Use sequential-thinking BETWEEN major phases** to validate progress
2. **Use cdq-* skills** for all Collibra operations:
   - Discovery: cdq-run-sql, cdq-list-tables
   - Onboarding: cdq-run-dq-job
   - Rules: cdq-save-rule, cdq-run-sql (for testing)
   - Validation: cdq-get-results, cdq-get-rules
3. **Track metrics throughout**: tables found → onboarded → rules created
4. **Test before saving**: Always validate with SQL queries
5. **Document failures**: Note tables/rules that fail
6. **Atomic operations**: Complete each table fully before next

---

## Success Criteria

✅ All "loan"/"customer" tables discovered and documented
✅ Each table onboarded with `AI_AUTO_ONBOARDED_*` naming
✅ Onboarding jobs validated as complete
✅ 5-10 domain-specific rules per table
✅ All rules tested and saved
✅ Complete audit trail via sequential-thinking checkpoints
```

### How to Use

1. Copy the prompt text above
2. Paste into Claude Code or your AI assistant
3. Enable sequential-thinking MCP server
4. Invoke cdq-* skills as directed
5. Let sequential-thinking track progress through all phases

---

## Example Prompt 1C: Automated Bank/Financial Table Discovery, Onboarding & DQ Rule Generation

**Use case:** Discover all tables containing "bank" in the name, onboard them as datasets, and generate domain-specific data quality rules for banking/regulatory data.

### Prompt Text

```
Use sequential-thinking to plan, analyze, and validate the following task:

## Task: Automated Bank/Financial Table Discovery, Onboarding & Data Quality Rule Generation

### Phase 1: Discovery & Preview
**Step 1.1: Find Bank Tables**
- Use cdq-list-tables or cdq-run-sql to search for tables with "bank" in the name
- Use SQL: `SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%bank%'`
- Use sequential-thinking to document all matching table names

**Step 1.2: Preview Each Table**
- For each discovered table, run: `SELECT * FROM <schema.table_name> LIMIT 5`
- Use cdq-run-sql for these queries (use actual schema.table names - e.g., samples.fdic_bank_institutions)
- Document schema: column names, data types, nullable fields
- Track data characteristics (patterns, ranges, domain logic)
- Get full column list: `SELECT STRING_AGG(column_name, ', ') FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '<table_name>'`

### Phase 2: Dataset Onboarding
**Step 2.1: Prepare Onboarding** (per table)
- Dataset name format: `AI_AUTO_ONBOARDED_<table_name>`
- SQL query: `SELECT * FROM <schema.table_name> LIMIT 10000`
- Log configuration for checkpoint

**Step 2.2: Execute Onboarding Jobs** (per table)
- Use cdq-run-dq-job to onboard each dataset
- Capture job IDs and timestamps
- Track in sequential-thinking

**Step 2.3: Validate Onboarding Success**
- Use cdq-get-results to check job completion
- Verify dataset ingestion (row count matches expected)
- Use sequential-thinking to validate each milestone
- Flag any failures for remediation

### Phase 3: Data Quality Rules Generation
**Step 3.1: Analyze Data for Rule Design** (per table)
- Review column types and distributions
- Identify data domain (banking/regulatory → FDIC IDs, names, assets, deposits, states)
- Use sequential-thinking to plan 5-10 domain-specific rules

**Step 3.2: Generate Rule Suggestions** (domain-specific categories)
Examples for bank/financial data:
- **Completeness**: NOT NULL on critical fields (fdic_certificate_number, institution_name, state_name, regulator)
- **Format**: Zip code 5-digit US format, state codes valid
- **Range**: total_assets >= 0, total_deposits >= 0
- **Consistency**: active flag not null, bank charter class valid
- **Domain Logic**: regulator in (N/A, FDIC, OCC, FRB, State), fdic_insured = Y/N

**Step 3.3: Test Each Rule**
- Use cdq-run-sql to validate rule syntax with: `SELECT COUNT(*) FROM <table_name> WHERE <rule_condition>`
- Example: `SELECT COUNT(*) FROM samples.fdic_bank_institutions WHERE total_assets < 0`
- Record pass/fail results

**Step 3.4: Save Rules**
- Use cdq-save-rule for each validated rule
- Associate with dataset: `AI_AUTO_ONBOARDED_<table_name>`
- Document rule name, description, SQL logic

### Phase 4: Completion & Validation
**Step 4.1: Generate Summary Report**
- Total tables discovered: ___
- Tables successfully onboarded: ___
- Total rules created and saved: ___
- Any failures or manual review needed: ___

**Step 4.2: Use Sequential-Thinking Final Validation**
- Confirm all steps completed in sequence
- Verify discovered tables vs. onboarded datasets
- Verify rule count per table (should be 5-10)
- Flag any gaps

---

## Execution Guidelines

1. **Use sequential-thinking BETWEEN major phases** to validate progress
2. **Use cdq-* skills** for all Collibra operations:
   - Discovery: cdq-run-sql, cdq-list-tables
   - Onboarding: cdq-run-dq-job
   - Rules: cdq-save-rule, cdq-run-sql (for testing)
   - Validation: cdq-get-results, cdq-get-rules
3. **Track metrics throughout**: tables found → onboarded → rules created
4. **Test before saving**: Always validate with SQL queries
5. **Document failures**: Note tables/rules that fail
6. **Atomic operations**: Complete each table fully before next

---

## Success Criteria

✅ All "bank" tables discovered and documented
✅ Each table onboarded with `AI_AUTO_ONBOARDED_*` naming
✅ Onboarding jobs validated as complete
✅ 5-10 domain-specific rules per table
✅ All rules tested and saved
✅ Complete audit trail via sequential-thinking checkpoints
```

### How to Use

1. Copy the prompt text above
2. Paste into Claude Code or your AI assistant
3. Enable sequential-thinking MCP server
4. Invoke cdq-* skills as directed
5. Let sequential-thinking track progress through all phases

---

## Example Prompt 2: Quick DQ Job with Inline Validation

**Use case:** Run a single DQ job, check results, propose rules, test and save them all with built-in checkpoints.

```
Use sequential-thinking step-by-step:

1. **Register Dataset** - Run cdq-run-dq-job:
   - Dataset: AI_TEST_CUSTOMERS
   - SQL: SELECT * FROM sales.customers LIMIT 25000
   - Track run-id returned

2. **Validate Job Completion** - Run cdq-get-results:
   - Use run-id from step 1
   - Verify job status is COMPLETE
   - Check data quality score

3. **Analyze Results** - Use sequential-thinking:
   - What rules are already attached?
   - What fields have high failure rates?
   - What domain makes sense? (CRM = email, phone validation, name format, etc.)

4. **Propose 3-5 Rules** - For each:
   - Test SQL first: `SELECT COUNT(*) FROM sales.customers WHERE {rule_condition}`
   - Use cdq-save-rule to persist
   - Document rule name and purpose

5. **Final Validation** - Run cdq-get-rules:
   - Verify all rules saved
   - Check rule count = step 4
```

---

## Example Prompt 3: Batch Onboarding Multiple Tables

**Use case:** Onboard a set of related tables (e.g., all HR tables) with consistent naming and rule patterns.

```
Use sequential-thinking to track multi-table onboarding:

**Setup**
- Table list: employees, departments, salaries, reviews, attendance
- Dataset prefix: AI_HR_
- SQL LIMIT: 50000
- Rules per table: 5-7 based on domain

**For each table:**
1. Preview (cdq-run-sql ... LIMIT 5)
2. Onboard (cdq-run-dq-job with AI_HR_<table_name>)
3. Validate (cdq-get-results)
4. Design rules (5-7 domain-specific)
5. Test rules (SQL COUNT queries)
6. Save rules (cdq-save-rule for each)
7. Checkpoint in sequential-thinking before next table

**Final Validation**
- Verify all tables onboarded (5 datasets)
- Verify total rules created (25-35)
- Confirm all rules saved
```

---

## Tips for Effective Multi-Step Prompts

### 1. **Use Phase Markers**
Break tasks into clearly labeled phases (Discovery, Onboarding, Validation, etc.). This helps both you and the AI track progress.

### 2. **Include Checkpoints**
Explicitly mark validation points:
```
**Checkpoint 1.2a**: Before proceeding, verify that all tables found
- Expected: 3-8 tables with 'employee' in name
- Actual: ___
- Proceed? [YES/NO]
```

### 3. **Specify Tool Usage**
Point to exact CDQ skills to use (not just "get data" but "use cdq-run-sql"):
- `cdq-run-sql` for direct queries against source tables
- `cdq-run-dq-job` for registering datasets
- `cdq-save-rule` for creating rules
- `cdq-get-results` for validation

### 4. **Include Limits and Safety**
Always specify query limits (LIMIT 5 for exploration, LIMIT 10000-50000 for onboarding):
```sql
-- SAFE for exploration
SELECT * FROM table_name LIMIT 5

-- SAFE for onboarding
SELECT * FROM table_name LIMIT 50000
```

### 5. **Use Domain Knowledge**
For data quality rules, tailor them to the data type:
- **Employees**: email validation, hire_date in past, salary > 0
- **Customers/Loan**: SSN format/required, email valid format, loan_rate 0-100%, car VIN 17-char, balance >= 0
- **Bank/Financial**: FDIC cert number required, institution name required, assets >= 0, deposits >= 0, zip 5-digit
- **Transactions**: amount > 0, date in range, status values limited

### 6. **Track Metrics**
Include clear counting throughout:
```
Phase 1 Result: Discovered 5 employee tables
Phase 2 Result: Onboarded 5 datasets
Phase 3 Result: Created 32 rules (6-7 per table on average)
```

---

## Integration with Sequential Thinking

### Prompt Structure for Max Clarity

```
[Your task description]

Use sequential-thinking to:
1. [First major step] - verify result
2. [Second major step] - validate assumptions
3. [Third major step] - test and confirm
...

After each major step, use sequential-thinking to:
- Document what succeeds
- Identify what failed
- Adjust approach if needed
- Confirm readiness for next step
```

### Example with Thinking Integration

```
Use cdq-run-dq-job to onboard the CUSTOMERS dataset:
- Dataset name: AI_AUDIT_CUSTOMERS
- SQL: SELECT * FROM sales.customers LIMIT 50000

After running, use sequential-thinking to:
- Confirm job completed (check status)
- Verify row count (should be close to 50000)
- Note any errors
- Decide: Ready for rule creation? [YES/NO]
```

---

## Common Patterns

### Pattern 1: Discover → Preview → Onboard → Validate
```
➀ Find tables (cdq-run-sql with LIKE filter)
➁ Preview each (cdq-run-sql LIMIT 5)
➂ Onboard (cdq-run-dq-job)
➃ Check results (cdq-get-results)
```

### Pattern 2: Analyze → Propose → Test → Save
```
➀ Get existing rules (cdq-get-rules)
➁ Propose new rules (sequential-thinking)
➂ Test SQL (cdq-run-sql with COUNT)
➃ Save rules (cdq-save-rule)
```

### Pattern 3: Batch Processing with Checkpoints
```
FOR each item in list:
  ➀ Process item
  ➁ Validate result (checkpoint)
  ➂ Save changes
END
➃ Summary report
```

---

## References

- **CDQ Skills Documentation**: See [README.md](./README.md) for full command reference
- **Sequential Thinking MCP**: [anthropic-ai/mcp-servers](https://github.com/anthropic-ai/mcp-servers)
- **Claude Code Guide**: `/help claude-code-guide` in Claude Code
- **Skill Creator Guide**: For building custom skills on top of these

---

## Troubleshooting Prompts

If a multi-step task fails:

1. **Identify which step failed** - Use sequential-thinking output to pinpoint
2. **Check assumptions** - Did you have the right table names? Connection? Limits?
3. **Test in isolation** - Run the failing cdq-* command directly to see error
4. **Adjust and retry** - Modify SQL, table name, or parameters based on error
5. **Document outcome** - Record what succeeded and what needs manual review

---

## Creating Your Own Multi-Step Prompts

Use this template:

```
Use sequential-thinking to plan, validate, and complete this task:

## Task: [Your task name]

### Objective
[Brief description of what you're trying to achieve]

### Phase 1: [Phase Name]
**Step 1.1: [Specific action]**
- Use [cdq-skill-name] to [action]
- Expected result: [what should happen]
- Checkpoint: [validate this before proceeding]

### Phase 2: [Phase Name]
...

### Success Criteria
✅ [Check 1]
✅ [Check 2]
✅ [Check 3]
```

Then follow these rules:
- One clear objective
- 2-4 phases maximum
- Each phase has 2-4 steps
- Each step names a cdq-* skill or sequential-thinking action
- Include checkpoints for validation
- List success criteria upfront
