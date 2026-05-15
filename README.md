# CDQ Skills

Platform-agnostic Claude Code skills for Collibra Data Quality (CDQ). These skills provide direct REST API access to CDQ without any MCP dependency, making them portable across AI ecosystems (Claude Code, Gemini CLI, and others).

> **Security Note:** This client uses standard environment variables (via dotenv) to connect to the CDQ API. It is intended for local, single-user use only. Do not expose this as a remote service without proper authentication, network controls, and encryption.

## CDQ Concepts

### Connection
A **Connection** represents a JDBC or cloud storage connection (BigQuery, Snowflake, S3, etc.) configured in CDQ and referenced by name (e.g., `BIGQUERY`).

### Dataset
A **Dataset** is a logical/virtual name within CDQ — NOT a `schema.table`. It can be any user-defined name like `DEMO_JOB` or `MY_CUSTOMERS`. A dataset is created by writing a source SQL query and registering it with a logical name. Rules and Alerts attach to **datasets**, not directly to database tables.

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
              Run Job ──► get-results
```

### Important Distinctions

| Command | Uses | Notes |
|---------|------|-------|
| `run-sql` | Strict `schema.table` | Direct database query — must use actual table names |
| `save-rule` | Dataset name (logical) | Attaches to registered dataset |
| `run-dq-job` | Dataset name (logical) | Registers and runs a dataset |
| `get-rules` | Dataset name (logical) | Retrieves rules for a dataset |
| `search-catalog` | N/A | Lists registered datasets with metadata |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/you/cdq-skills.git
cd cdq-skills
pip install -e .

# 2. Copy environment template and configure
cp .env.example .env
# Edit .env with your credentials

# 3. Test connection
cdq test-connection
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DQ_URL` | Base URL for Collibra DQ API | Yes |
| `DQ_USERNAME` | Username for authentication | Yes |
| `DQ_PASSWORD` | Password for authentication | Yes |
| `DQ_ISS` | Tenant identifier | Yes |
| `DQ_CXN` | Default datasource connection | No (default: BIGQUERY) |
| `DQ_VERIFY_SSL` | Set to `false` for self-signed certs | No (default: true) |

---

## Available Commands

### Single Commands

| Command | Description |
|---------|-------------|
| `cdq test-connection` | Verify API credentials |
| `cdq run-sql` | Execute SQL against datasource (physical table names) |
| `cdq list-tables` | List physical tables in a schema |
| `cdq search-catalog` | Search registered datasets in catalog |
| `cdq run-dq-job` | Register dataset and run DQ job |
| `cdq get-jobs` | List queued DQ jobs |
| `cdq get-dataset` | Get dataset definition |
| `cdq get-results` | Get DQ job results |
| `cdq get-rules` | Get DQ rules for a dataset |
| `cdq save-rule` | Create a new DQ rule |
| `cdq get-alerts` | Get alerts for a dataset |
| `cdq save-alert` | Create a new alert |
| `cdq get-recent-runs` | Get recent DQ job run IDs |

### Workflow Skills (Claude Code slash commands)

| Skill | Description |
|-------|-------------|
| `/cdq-workflow-explore-dataset` | Search catalog, identify columns, sample data |
| `/cdq-workflow-run-complete-job` | Explore, run job, check status, get results |
| `/cdq-workflow-save-complete-rule` | Explore, confirm, then save a DQ rule |
| `/cdq-workflow-suggest-rules` | Analyze columns and propose rules based on patterns |

---

## Usage

### Typical Workflow

```bash
# 1. Test your query first with actual table name
cdq run-sql --sql "SELECT * FROM actual_schema.actual_table LIMIT 10"

# 2. Register a dataset with a logical name
cdq run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM actual_schema.actual_table WHERE active = true"

# 3. Add rules to the dataset
cdq save-rule \
  --dataset "MY_DATASET" \
  --name "Email Check" \
  --sql "SELECT * FROM {dataset} WHERE email IS NULL"

# 4. Check results
cdq get-results --dataset "MY_DATASET" --run-id "2025-03-09"
```

### Common Workflows

```bash
# Explore a table
cdq search-catalog --query "nyse"
cdq run-sql --sql "SELECT * FROM samples.nyse_categorical LIMIT 5"
cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.nyse_categorical"

# Run a DQ job
cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM schema.table LIMIT 100000"
cdq get-jobs --limit 3
cdq get-results --dataset "MY_DATASET" --run-id "2026-03-09"

# Add rules and re-run
cdq save-rule --dataset "CUSTOMER_DATA" --name "No Null Emails" \
  --sql "SELECT * FROM {dataset} WHERE email IS NULL"
cdq run-dq-job --dataset "CUSTOMER_DATA" --sql "SELECT * FROM sales.customers LIMIT 50000"

# Set up alerts
cdq save-alert --dataset "MY_DATASET" --name "Low Quality Alert" \
  --condition "score < 90" --email "team@company.com"
cdq get-alerts --dataset "MY_DATASET"
```

---

## Linking Skills to Claude Code

```bash
# Project-specific (recommended)
mkdir -p .claude/skills
ln -s /path/to/cdq-skills/.claude/skills/* .claude/skills/

# Or global (all projects)
ln -s /path/to/cdq-skills/.claude/skills/* ~/.claude/skills/
```

---

## Project Structure

```
cdq-skills/
├── .env.example              # Template environment file
├── pyproject.toml            # Package definition (installs cdq CLI)
├── requirements.txt          # Python dependencies
├── cdq_skills/               # Main package
│   ├── auth.py               # Auth module (token caching)
│   └── client.py             # CLI entry point
└── .claude/skills/           # Claude Code skills
    ├── lib/
    │   ├── skill_wrapper.py  # Shared wrapper module
    │   └── NAMING.md         # Logical vs physical name reference
    ├── cdq-test-connection/
    ├── cdq-run-sql/
    ├── cdq-run-dq-job/
    ├── cdq-get-results/
    ├── cdq-get-rules/
    ├── cdq-save-rule/
    ├── cdq-get-alerts/
    ├── cdq-save-alert/
    ├── cdq-search-catalog/
    ├── cdq-list-tables/
    ├── cdq-get-jobs/
    ├── cdq-get-dataset/
    ├── cdq-get-recent-runs/
    ├── cdq-workflow-explore-dataset/
    ├── cdq-workflow-run-complete-job/
    ├── cdq-workflow-save-complete-rule/
    └── cdq-workflow-suggest-rules/
```

---

## Authentication

The client authenticates via `/auth/signin`:
1. POST with `{username, password, iss}`
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

**SSL Certificate Error** — add `DQ_VERIFY_SSL=false` to `.env`

**Authentication Error** — verify `DQ_USERNAME`, `DQ_PASSWORD`, and `DQ_ISS` in `.env`

**Empty Results** — use `cdq search-catalog --query ""` to list all datasets; use `cdq get-recent-runs` to find valid run IDs

## License

MIT
