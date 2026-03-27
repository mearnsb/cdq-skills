# CDQ Skills

Platform-agnostic Claude Code skills for Collibra Data Quality (CDQ). These skills provide direct REST API access to CDQ without any MCP dependency, making them portable across AI ecosystems (Claude Code, OpenClaw, Gemini CLI, OpenCode, etc.).

> **Security Note:** This client uses standard environment variables (via dotenv) to connect to the CDQ API. It is intended for local, single-user use only (similar to Claude Code and OpenClaw). Do not expose this as a remote service unless you understand the security implications and have proper authentication, network controls, and encryption in place.

## CDQ Concepts

Understanding these core concepts is essential for working with CDQ:

### Connection
A **Connection** represents a JDBC or cloud storage connection (BigQuery, Snowflake, S3, GCS, etc.) that provides access to underlying data sources. Connections are configured in CDQ and referenced by name (e.g., `BIGQUERY`, `SNOWFLAKE`).

### Dataset
A **Dataset** is a logical/virtual name within CDQ - NOT necessarily a `schema.table` or fully qualified name. While it often mirrors the source table name (e.g., `samples.nyse_categorical`), it can be any user-defined name like:
- `DEMO_JOB`
- `TEST_RUN`
- `SAMPLE_XYZ`
- `my_project.customers`

A dataset is created by:
1. Writing a source SQL query (or pointing to a file)
2. Registering it with a logical name
3. The query defines what data the dataset contains

**Key point:** Rules and Alerts attach to **datasets** (logical names), not directly to database tables.

### Rule
A **Rule** defines a data quality check attached to a dataset. Rules use SQL to identify problem records - any rows returned represent failures.

### Alert
An **Alert** monitors a dataset and triggers notifications when conditions are met (e.g., score drops below threshold).

### Job
A **Job** is created when a dataset is run. Executing a dataset runs all attached rules and produces results.

### Results
**Results** (also called "hoot") are produced when a job completes, containing scores, pass/fail counts, and findings for each rule.

### The Workflow

```
Connection ──► Source Data (schema.table)
                     │
                     ▼
              Source SQL Query ──► run-sql (test/query)
                     │
                     ▼
              Register Dataset ──► run-dq-job (creates logical name)
                     │
                     ▼
              Attach Rules/Alerts ──► save-rule, save-alert
                     │
                     ▼
              Run Job ──► Job executes rules
                     │
                     ▼
              Get Results ──► get-results
```

### Important Distinctions

| Concept | Uses | Notes |
|---------|------|-------|
| `run-sql` | Strict `schema.table` | Direct database query - must use actual table names |
| `save-rule` | Dataset name (logical) | Attaches to registered dataset |
| `run-dq-job` | Dataset name (logical) | Registers and runs a dataset |
| `get-rules` | Dataset name (logical) | Retrieves rules for a dataset |
| `search-catalog` | N/A | Lists registered datasets with metadata |

---

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your credentials
# DQ_URL=https://your-collibra-dq-instance.com
# DQ_USERNAME=your_username
# DQ_PASSWORD=your_password
# DQ_ISS=your_tenant
# DQ_CXN=BIGQUERY
# DQ_VERIFY_SSL=false  # For self-signed certs

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test connection
python lib/client.py test-connection
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DQ_URL` | Base URL for Collibra DQ API | Yes |
| `DQ_USERNAME` | Username for authentication | Yes |
| `DQ_PASSWORD` | Password for authentication | Yes |
| `DQ_ISS` | Tenant identifier | Yes |
| `DQ_CXN` | Default datasource connection | No (default: BIGQUERY) |
| `DQ_VERIFY_SSL` | Set to `false` for self-signed certs | No (default: true) |

## Available Skills

### Single Commands

| Skill | Description |
|-------|-------------|
| `cdq-run-sql` | Execute SQL queries against datasource (uses actual table names) |
| `cdq-get-rules` | Get DQ rules for a dataset (logical name) |
| `cdq-save-rule` | Create a new DQ rule for a dataset (logical name) |
| `cdq-run-dq-job` | Register dataset and run DQ job (creates logical name) |
| `cdq-search-catalog` | Search registered datasets in catalog |
| `cdq-get-jobs` | List queued DQ jobs |
| `cdq-get-dataset` | Get dataset definition |
| `cdq-get-results` | Get DQ job results (hoot) |
| `cdq-get-alerts` | Get alerts for a dataset (logical name) |
| `cdq-save-alert` | Create a new alert for a dataset (logical name) |
| `cdq-get-recent-runs` | Get recent DQ job runs |
| `cdq-list-tables` | List physical tables in a schema (via INFORMATION_SCHEMA) |

### Workflows (Multi-step)

| Skill | Description |
|-------|-------------|
| `cdq-workflow-explore-dataset` | Explore table - search catalog, identify columns, sample data (LIMIT 5) |
| `cdq-workflow-run-complete-job` | Full workflow - explore, run job, check status, get results |
| `cdq-workflow-save-complete-rule` | Explore, confirm, then save a DQ rule |
| `cdq-workflow-suggest-rules` | Analyze columns and propose rule types based on patterns |

## Usage

### Typical Workflow

```bash
# 1. Test your query first with actual table name
python lib/client.py run-sql --sql "SELECT * FROM actual_schema.actual_table LIMIT 10"

# 2. Register a dataset with a logical name
python lib/client.py run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM actual_schema.actual_table WHERE active = true" \
  --run-id "2025-03-09"

# 3. Add rules to the dataset
python lib/client.py save-rule \
  --dataset "MY_DATASET" \
  --name "Email Check" \
  --sql "SELECT * FROM {dataset} WHERE email IS NULL"

# 4. Check results
python lib/client.py get-results --dataset "MY_DATASET" --run-id "2025-03-09"
```

## Common Workflows

### Explore and Identify a Table

Find a table, explore its schema, and understand the data before running a job.

```bash
# 1. Search catalog for the table
python lib/client.py search-catalog --query "nyse"

# 2. Identify columns + sample data (LIMIT 5 - always limit for exploration)
python lib/client.py run-sql --sql "SELECT * FROM samples.nyse_categorical LIMIT 5"

# 3. Get row count
python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM samples.nyse_categorical"
```

### Run DQ Job with Safe Limits

Run a complete job with appropriate limits to ensure safety.

```bash
# 1. Run DQ job with LIMIT (default: 100,000)
python lib/client.py run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM schema.table LIMIT 100000"

# 2. Check job status
python lib/client.py get-jobs --limit 3

# 3. Get results (use the run-id from step 1)
python lib/client.py get-results --dataset "MY_DATASET" --run-id "2026-03-09"
```

### Run Job, Check Results, Add Rule

Typical cycle: run job → review results → add rules → run again.

```bash
# Run job
python lib/client.py run-dq-job \
  --dataset "CUSTOMER_DATA" \
  --sql "SELECT * FROM sales.customers LIMIT 50000"

# Get results
python lib/client.py get-results --dataset "CUSTOMER_DATA" --run-id "2026-03-09"

# Add a rule based on findings
python lib/client.py save-rule \
  --dataset "CUSTOMER_DATA" \
  --name "No Null Emails" \
  --sql "SELECT * FROM {dataset} WHERE email IS NULL"

# Run again to apply new rule
python lib/client.py run-dq-job \
  --dataset "CUSTOMER_DATA" \
  --sql "SELECT * FROM sales.customers LIMIT 50000"
```

### Set Up Alerts

Add monitoring to a dataset.

```bash
# Create alert for low score
python lib/client.py save-alert \
  --dataset "MY_DATASET" \
  --name "Low Quality Alert" \
  --condition "score < 90" \
  --email "team@company.com"

# Get existing alerts
python lib/client.py get-alerts --dataset "MY_DATASET"
```

---

### All Commands

```bash
# Test connection
python lib/client.py test-connection

# Search catalog for registered datasets
python lib/client.py search-catalog --query "" --limit 10

# Get rules for a dataset
python lib/client.py get-rules --dataset "MY_DATASET"

# Create a rule
python lib/client.py save-rule \
  --dataset "MY_DATASET" \
  --name "Email Not Null" \
  --sql "SELECT * FROM {dataset} WHERE email IS NULL"

# Run DQ job
python lib/client.py run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM source_table" \
  --run-id "2025-03-09"

# Get results
python lib/client.py get-results \
  --dataset "MY_DATASET" \
  --run-id "2025-03-09"

# Run SQL directly (uses actual table names)
python lib/client.py run-sql --sql "SELECT COUNT(*) FROM schema.table"

# Get recent runs
python lib/client.py get-recent-runs

# Get jobs in queue
python lib/client.py get-jobs --limit 20

# Create alert
python lib/client.py save-alert \
  --dataset "MY_DATASET" \
  --name "Low Score Alert" \
  --condition "score < 90" \
  --email "team@company.com"
```

## Platform Differences

These skills work across multiple AI coding assistants, but invocation differs:

### Claude Code

| Feature | Details |
|---------|---------|
| Skill path | `.claude/skills/` |
| Invocation | `/skill-name --args` |
| Auto-discovery | Yes (reads `.claude/skills/`) |
| Permissions | Prompts for tool approval |

```bash
# Claude Code uses slash commands
/cdq-search-catalog --query ""
/cdq-get-rules --dataset "MY_DATASET"
/cdq-run-sql --sql "SELECT COUNT(*) FROM schema.table"
```

### Gemini CLI

| Feature | Details |
|---------|---------|
| Skill path | `.gemini/skills/` |
| Invocation | `skill-name --args` (no slash) |
| Auto-discovery | Yes (reads `.gemini/skills/`) |
| Permissions | May require explicit approval |

```bash
# Gemini CLI - no slash prefix
cdq-search-catalog --query ""
cdq-get-rules --dataset "MY_DATASET"
cdq-run-sql --sql "SELECT COUNT(*) FROM schema.table"
```

### OpenClaw

| Feature | Details |
|---------|---------|
| Skill path | `.claw/skills/` or `~/.claw/skills/` |
| Invocation | `/skill-name` or direct command |
| Auto-discovery | Yes (skill-compatible format) |
| Permissions | Configurable |

```bash
# OpenClaw - similar to Claude Code
/cdq-search-catalog --query ""
```

### OpenCode / Other Agents

| Feature | Details |
|---------|---------|
| Skill path | Varies by agent |
| Invocation | Often direct CLI execution |
| Auto-discovery | May require manual config |

For agents without skill discovery, run skills directly:

```bash
# Direct execution (works everywhere)
python lib/client.py search-catalog --query ""
python lib/client.py get-rules --dataset "MY_DATASET"
python lib/client.py run-sql --sql "SELECT COUNT(*) FROM schema.table"
```

### Compatibility Notes

1. **Skill Format**: All skills use the same `SKILL.md` + `lib/client.py` structure - compatible across platforms
2. **CLI Arguments**: All commands work with direct `python lib/client.py` invocation
3. **Environment**: All platforms require `.env` with CDQ credentials
4. **Permissions**: Claude Code prompts per-tool; others may auto-approve or require config

## Project Structure

```
cdq-skills/
├── .env.example          # Template environment file
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── tests/
│   └── test_skills.py    # Fast skill tests (22 tests, <30s)
├── lib/
│   ├── auth.py           # Auth module (/auth/signin token caching)
│   └── client.py         # CLI wrapper for all operations
└── .claude/skills/
    ├── lib/
    │   └── skill_wrapper.py  # Shared wrapper (consolidated)
    # Command Skills (13)
    ├── cdq-test-connection/
    ├── cdq-search-catalog/
    ├── cdq-list-tables/
    ├── cdq-run-sql/
    ├── cdq-run-dq-job/
    ├── cdq-get-dataset/
    ├── cdq-get-rules/
    ├── cdq-get-results/
    ├── cdq-get-alerts/
    ├── cdq-get-jobs/
    ├── cdq-get-recent-runs/
    ├── cdq-save-rule/
    ├── cdq-save-alert/
    # Workflow Skills (4)
    ├── cdq-workflow-explore-dataset/
    ├── cdq-workflow-run-complete-job/
    ├── cdq-workflow-save-complete-rule/
    └── cdq-workflow-suggest-rules/
        └── references/
            ├── rule-patterns.md
            └── safety-limits.md
```

### Skill Structure

Each skill has a consistent structure:

```
cdq-<name>/
├── SKILL.md           # Documentation (usage, examples, API endpoint)
├── lib/
│   └── client.py      # 6-line wrapper using shared skill_wrapper module
```

The shared `skill_wrapper.py` consolidates duplicated wrapper logic, reducing each skill's wrapper from ~38 lines to 6 lines.

## Multi-Step Task Workflows

For complex, multi-step CDQ tasks that require planning, validation, and progress tracking, see **[EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md)**.

This guide provides:
- **Structured prompt templates** for common workflows (discovery, onboarding, rule generation)
- **Sequential-thinking integration** for task planning and validation across steps
- **Best practices** for batch processing, checkpoints, and failure handling
- **Custom prompt templates** you can adapt for your own tasks

### Full Example: Claims Table Discovery, Onboarding & Rule Generation

**Use case:** Discover all claims-related tables, onboard them as datasets, and generate domain-specific data quality rules with validation checkpoints.

**Prompt:**

```
Use sequential-thinking to plan, analyze, and validate the following task:

## Task: Automated Claims Table Discovery, Onboarding & Data Quality Rule Generation

### Objective
Discover all tables containing "claims" in their name, onboard them as datasets with standardized naming,
generate domain-specific data quality rules, and validate the complete pipeline.

---

### Phase 1: Discovery & Preview

**Step 1.1: Find Claims Tables**
- Use cdq-run-sql to search database schema
- SQL: SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%claims%'
- Use sequential-thinking to document all matching table names
- Record full schema names (schema.table_name)

**Step 1.2: Preview Each Table**
- For each discovered table, run: SELECT * FROM <schema.table_name> LIMIT 5
- Use cdq-run-sql for direct queries (use actual table names)
- Document schema: column names, data types, nullability
- Note data characteristics:
  - Date fields (claim_date, incident_date, submission_date, decision_date)
  - Amount fields (claim_amount, deductible, coverage_limit)
  - Status/code fields (status, claim_type, adjuster_id)
  - Reference fields (policy_id, claimant_id, incident_id)

---

### Phase 2: Dataset Onboarding

**Step 2.1: Prepare Onboarding Configuration** (for each table)
- Dataset name format: AI_AUTO_ONBOARDED_<table_name>
- SQL query: SELECT * FROM <schema.table_name> LIMIT 10000
- Record configuration for validation checkpoint
- Document expected row count range

**Step 2.2: Execute Onboarding Jobs** (per table)
- Use cdq-run-dq-job to trigger dataset onboarding
- Example: dataset="AI_AUTO_ONBOARDED_claims", sql="SELECT * FROM insurance.claims LIMIT 10000"
- Monitor job execution and capture job IDs
- Record timestamps and any warnings

**Step 2.3: Validate Onboarding Success**
- Use cdq-get-results to check each job's completion status
- Verify:
  - Job status = COMPLETE (or SUCCESS)
  - Actual row count is within expected range (not 0, not truncated)
  - All columns from preview are present in dataset
- Use sequential-thinking to validate each job milestone
- Flag any failures for manual remediation

---

### Phase 3: Data Quality Rules Generation

**Step 3.1: Analyze Claims Data for Rule Design** (per table)
- Review column types, distributions, sample values
- Identify claims domain specifics:
  - Date sequences (claim_date should be before submission_date, both before decision_date)
  - Amount validations (claim_amount > 0, within typical range 100-100000)
  - Status/type enumerations (OPEN, APPROVED, REJECTED, PENDING, CLOSED, etc.)
  - Reference integrity (policy_id, claimant_id must exist in related tables or be non-null)
  - Required fields (claim_id, claimant_id, claim_date are critical)
- Use sequential-thinking to plan 5-10 domain-specific rules

**Step 3.2: Generate Rule Suggestions** (Domain-specific for claims)

Generate these rule categories:

- **Completeness (NOT NULL)**
  - claim_id must not be null
  - claimant_id must not be null
  - claim_date must not be null
  - claim_amount must not be null
  - status must not be null

- **Uniqueness**
  - claim_id must be unique (no duplicate claims)
  - claim_no (if exists) must be unique

- **Format & Pattern**
  - claim_id should match format (e.g., starts with "CLM-" or numeric-only)
  - claimant_email (if exists) must match email pattern
  - phone_number (if exists) must be 10 digits for US
  - policy_id must match known format

- **Range & Logic**
  - claim_amount must be > 0
  - claim_amount must be <= policy_coverage_limit
  - claim_date must not be in future
  - incident_date must not be in future
  - adjuster_assigned_date must be >= claim_received_date (if both exist)
  - submission_date must be >= incident_date

- **Referential Integrity**
  - claim_type must be in (MEDICAL, AUTO, PROPERTY, LIABILITY, WORKERS_COMP, etc.)
  - status must be in (OPEN, APPROVED, REJECTED, PENDING, CLOSED, APPEAL, DENIED, etc.)
  - adjuster_id should reference valid adjuster IDs
  - policy_id should reference valid policies

- **Consistency**
  - If status = CLOSED, then close_date must not be null
  - If status = APPROVED, then approval_date must be <= current_date
  - claimant_age must be >= 18 (if applicable)
  - deductible must be <= claim_amount

**Step 3.3: Test Each Rule** (validate syntax & logic)
- Pick 3-4 rules to test first
- For each rule, use cdq-run-sql with COUNT to validate:
  - Example: SELECT COUNT(*) FROM <table_name> WHERE claim_amount <= 0 (should find violations)
  - Example: SELECT COUNT(*) FROM <table_name> WHERE claim_id IS NULL (should be 0 for valid data)
  - Use LIMIT 1000 if testing on large datasets
- Verify rule captures expected violations
- Adjust SQL as needed for database dialect
- Record pass/fail results in sequential-thinking

**Step 3.4: Save Rules** (per table)
- Use cdq-save-rule to persist each validated rule
- Associate rule with dataset: AI_AUTO_ONBOARDED_<table_name>
- For each rule provide:
  - Rule name (descriptive, e.g., "Claim Amount Must Be Positive")
  - Rule description (business logic, e.g., "Claim amounts must be greater than zero")
  - SQL condition (the WHERE clause that identifies failures)
- Document all 5-10 rules created per table

---

### Phase 4: Completion & Validation

**Step 4.1: Generate Summary Report**
- Total claims tables discovered: ___
- Tables successfully onboarded: ___
- Total rules created and saved: ___
- Failures or manual review needed: ___
- Average rules per table: ___ (target: 5-10)

**Step 4.2: Final Validation Checkpoint**
- Use sequential-thinking to confirm:
  - ✅ All discovered tables appear in onboarded datasets
  - ✅ All onboarding jobs completed successfully
  - ✅ All rules tested and validated
  - ✅ Rule count per table is 5-10 (adjust if needed)
  - ✅ All rules saved and associated with correct datasets
- Cross-check discovered tables vs. onboarded datasets (count must match)
- Verify rule count per table (should be consistent across similar tables)
- Flag any gaps for remediation

---

## Execution Guidelines

1. **Use sequential-thinking BETWEEN major phases** to validate progress
2. **Use cdq-* skills** for all Collibra operations:
   - Discovery: cdq-run-sql, cdq-list-tables
   - Onboarding: cdq-run-dq-job (with dataset="AI_AUTO_ONBOARDED_*", LIMIT 10000)
   - Rules: cdq-save-rule, cdq-run-sql (for testing)
   - Validation: cdq-get-results, cdq-get-rules
3. **Track metrics throughout**: tables found → onboarded → rules created
4. **Test before saving**: Always validate SQL with COUNT queries
5. **Document failures**: Use sequential-thinking to note any tables/rules that fail
6. **Atomic operations**: Complete each table fully before moving to next

---

## Success Criteria

✅ All "claims" tables discovered and documented
✅ Each table onboarded with AI_AUTO_ONBOARDED_<table_name> naming
✅ Onboarding jobs validated as complete (status, row count, columns)
✅ 5-10 domain-specific rules per claims table
✅ All rules tested and saved
✅ Complete audit trail via sequential-thinking checkpoints
✅ Summary report showing metrics (tables, rules, success rate)
```

**See [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md)** for additional examples (employees, batch processing patterns, and custom prompt templates).

---

## Testing

Run the test suite to verify all skills are working:

```bash
python tests/test_skills.py
```

Tests cover:
- Wrapper structure (13 skills)
- Wrapper imports (spot check)
- Command execution (6 core commands)

## Linking Skills to Your Workspace

### For Claude Code

```bash
# Project-specific (recommended)
mkdir -p .claude/skills
ln -s /path/to/cdq-skills/.claude/skills/* .claude/skills/

# Or global (all projects)
ln -s /path/to/cdq-skills/.claude/skills ~/.claude/skills/cdq-skills
```

### For Gemini CLI

```bash
# Project-specific
mkdir -p .gemini/skills
ln -s /path/to/cdq-skills/.claude/skills/cdq-* .gemini/skills/

# Or global
ln -s /path/to/cdq-skills/.claude/skills/cdq-* ~/.gemini/skills/
```

### For OpenClaw

```bash
# Project-specific
mkdir -p .claw/skills
ln -s /path/to/cdq-skills/.claude/skills/cdq-* .claw/skills/
```

### Alternative: Copy Instead of Link

```bash
# Claude Code - copy all skills
cp -r /path/to/cdq-skills/.claude/skills/* ~/.claude/skills/

# Gemini CLI - copy command skills only
cp -r /path/to/cdq-skills/.claude/skills/cdq-* ~/.gemini/skills/
```

---

## Authentication

The client authenticates via `/auth/signin` endpoint:
1. POST to `/auth/signin` with `{username, password, iss}`
2. Receives `{token: "..."}`
3. Uses `Bearer <token>` for subsequent requests
4. Token is cached in memory for ~1 hour

## API Endpoints

| Command | Endpoint | Method |
|---------|----------|--------|
| `run-sql` | `/v2/getsqlresult` | POST |
| `get-rules` | `/v3/rules/{dataset}` | GET |
| `save-rule` | `/v3/rules` | POST |
| `run-dq-job` | `/v3/datasetDefs` + `/v3/jobs/run` | PUT + POST |
| `search-catalog` | `/v2/getdataassetsarrforserversidewithmultifilters` | GET |
| `get-jobs` | `/v2/getowlcheckq` | GET |
| `get-dataset` | `/v2/owl-options/get` | GET |
| `get-results` | `/v2/gethoot` | GET |
| `get-alerts` | `/v2/getalerts` | GET |
| `save-alert` | `/v3/alerts` | POST |
| `get-recent-runs` | `/v2/getrecentruns` | GET |

## Troubleshooting

### SSL Certificate Error

If you see `SSL: CERTIFICATE_VERIFY_FAILED`, add to your `.env`:
```
DQ_VERIFY_SSL=false
```

### Authentication Error

1. Verify `DQ_USERNAME` and `DQ_PASSWORD` are correct
2. Ensure `DQ_ISS` matches your tenant identifier
3. Check that your account has API access

### Empty Results

- For `search-catalog`, use empty query `--query ""` to list all datasets
- Some endpoints require specific run IDs - use `get-recent-runs` first

## Custom Notes and Reference Lists

If you need to add project-specific notes, table references, or additional documentation that should be available to Claude, you can use:

### CLAUDE.md (Recommended for Claude Code)

Create a `CLAUDE.md` file in your project root. Claude automatically reads this file and uses it as context.

```markdown
# Project Notes

## Table Reference
- samples.accounts - User financial accounts
- samples.orders - Transaction history
- samples.customers - Customer master data

## Custom DQ Rules
- Our standard threshold is 95% for all datasets
- Email validation rules go in the customers dataset
```

### docs/tables.md (For detailed references)

Create a dedicated documentation file for tables, schemas, or domain-specific notes:

```markdown
# Database Table Reference

## samples schema

| Table | Description | Columns |
|-------|-------------|---------|
| accounts | User accounts | id, name, email, created_at |
| orders | Orders | order_id, customer_id, total, status |

## production schema

| Table | Description |
|-------|-------------|
| transactions | Financial transactions |
```

### Using with Multiple AI Tools

These markdown files work across different AI assistants:
- **Claude Code** - Reads CLAUDE.md automatically
- **Gemini CLI** - Also supports CLAUDE.md
- **OpenClaw** - Supports markdown reference files
- **Other tools** - You can share these reference files directly

### When to Use Reference Lists

- INFORMATION_SCHEMA is not accessible (restricted permissions)
- You want to document domain-specific table meanings
- Sharing tribal knowledge about data structures
- Adding notes about custom transformations or business rules

## License

MIT