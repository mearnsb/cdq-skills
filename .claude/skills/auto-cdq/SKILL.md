---
name: auto-cdq
description: "CDQ workflow wizard. Use: /auto-cdq [discovery|onboarding|rules] [--schema SCHEMA] [--table TABLE] [--dataset DATASET] [--limit N]"
run: python3 .claude/bin/auto-cdq-wizard.py
---

# Auto-CDQ — Interactive Wizard

An interactive, autoresearch-style wizard for Collibra DQ workflows. Orchestrates existing CDQ skills to guide users through schema selection, table discovery, onboarding, and rule creation.

## Overview

The auto-cdq wizard is a **standalone orchestrator** that:

- Runs the `.claude/bin/auto-cdq-wizard.py` script
- Guides users through three main workflows: Discovery, Onboarding, Rules
- Calls existing CDQ skills internally (via `/cdq-run-sql`, `/cdq-run-dq-job`, etc.)
- Stores progress in `.auto-cdq-state.json` for backward navigation
- **Leaves all public-repo CDQ skills completely unchanged**

All individual CDQ skills remain available as standalone commands:
- `/cdq-search-catalog` — Search datasets
- `/cdq-list-tables` — List tables
- `/cdq-run-sql` — Execute SQL queries
- `/cdq-run-dq-job` — Run DQ jobs
- `/cdq-save-rule` — Create rules
- ...and 10+ more

---

## Usage

### Show workflow menu (interactive)
```bash
/auto-cdq
# Displays numbered menu for Discovery, Onboarding, Rules, or Exit
```

### Discovery Workflow
```bash
/auto-cdq discovery                                          # Interactive discovery
/auto-cdq discovery --schema samples                         # Specify schema
/auto-cdq discovery --schema samples --table accounts        # Pre-select table
/auto-cdq discovery --schema samples --table accounts --limit 10  # Set preview rows
```

### Onboarding Workflow
```bash
/auto-cdq onboarding                                          # Interactive onboarding
/auto-cdq onboarding --schema samples --table accounts        # Specify data source
/auto-cdq onboarding --dataset customers_dq                  # Set logical dataset name
/auto-cdq onboarding --schema samples --table accounts --dataset accounts_dq --limit 50000  # Full config
```

### Rules Workflow
```bash
/auto-cdq rules                                               # Interactive rule creation
/auto-cdq rules --dataset customers_dq                       # Work with existing dataset
```

---

## Workflows

### 1. Discovery Workflow
**Find and preview tables** with guided search.

Flow:
1. Select schema (or use configured default)
2. Search or browse tables
3. Preview data (5 rows)
4. Choose next step (Onboarding, Rules, or continue discovery)

### 2. Onboarding Workflow
**Register a dataset** and run a DQ job.

Flow:
1. Specify dataset name (suggested: `{table}_dq`)
2. Choose data size limit (1K, 10K, 50K, 100K, or full)
3. Test connection to CDQ
4. Run DQ job
5. Check results

### 3. Rules Workflow
**Analyze data and create data quality rules**.

Flow:
1. Analyze columns for patterns (powered by `/cdq-workflow-suggest-rules`)
2. Review and select suggested rules (HIGH/MEDIUM/LOW priority)
3. Test rules against data
4. Save validated rules to dataset

---

## Architecture

### State Management
Progress is saved to `.auto-cdq-state.json`:
- Persists across turns
- Enables backward navigation (user can modify earlier choices)
- Cleared on exit or error

### Backend Integration
The wizard delegates real work to existing CDQ skills:

| Operation | Skill Called |
|-----------|--------------|
| Test connection | `/cdq-test-connection` |
| List tables | `/cdq-list-tables` |
| Preview data | `/cdq-run-sql` |
| Run DQ job | `/cdq-run-dq-job` |
| Get results | `/cdq-get-results` |
| Suggest rules | `/cdq-workflow-suggest-rules` |
| Save rule | `/cdq-save-rule` |

All skills run unchanged, unaware they're being called by the wizard.

### Implementation
- **Wizard script**: `.claude/bin/auto-cdq-wizard.py`
- **Configuration**: Reads from project environment (DQ_URL, DQ_USER, etc.)
- **Logging**: Uses `.auto-cdq-state.json` for state tracking

---

## User Experience

The wizard presents numbered menus for each choice:

```
AUTO-CDQ WIZARD: Workflow Selection
==================================================================

1) Discovery (Recommended)     — Find and preview tables with guided search
2) Onboarding                   — Register a dataset and run a DQ job
3) Rules                        — Analyze data and create quality rules
4) Exit                         — Finish the session

Choose an option (1-4):
→ _
```

After selecting a workflow, you're guided through each phase with clear prompts and options.

---

## Key Features

✅ **Multi-phase workflows** — Discovery → Onboarding → Rules (or pick any starting point)

✅ **Backward navigation** — Modify earlier choices without restarting

✅ **State persistence** — Progress saved, survives restarts

✅ **Real backend calls** — Uses existing CDQ skills, not mock data

✅ **Safe defaults** — Recommended options, clear descriptions

✅ **Error handling** — Connection failures lead to `/cdq-test-connection`, not dead ends

✅ **No Python changes to existing skills** — All public-repo skills stay unchanged

---

## Tips

- **Show menu?** Type `/auto-cdq` with no arguments to see interactive workflow selection.
- **Quick discovery?** Use `/auto-cdq discovery --schema samples --table accounts --limit 10`
- **Pre-configure onboarding?** Use `/auto-cdq onboarding --schema samples --table accounts --dataset accounts_dq`
- **Work with existing dataset?** Use `/auto-cdq rules --dataset mydata_dq` to create rules
- **Use individual skills?** All 15+ CDQ skills work standalone: `/cdq-search-catalog`, `/cdq-run-sql`, etc.

---

## Troubleshooting

### Connection failures
If the wizard can't reach CDQ:
1. The wizard will run `/cdq-test-connection`
2. Check your `.env` file for `DQ_URL`, `DQ_USER`, `DQ_PASSWORD`
3. Verify network connectivity to the CDQ server

### No tables found
If a schema search returns 0 results:
1. Try a different schema
2. Use `/cdq-list-tables --schema <name>` directly to debug
3. Verify the table exists in your datasource

### SQL errors
If a preview or job fails:
1. The error message will show the problematic query
2. Try `/cdq-run-sql --sql "SELECT * FROM ..."` directly to test
3. Modify your schema/table selection and retry

---

## See Also

- `/cdq-search-catalog` — Search for existing datasets
- `/cdq-list-tables` — List tables in a schema
- `/cdq-run-sql` — Execute SQL queries directly
- `/cdq-run-dq-job` — Register dataset and run job
- `/cdq-save-rule` — Create data quality rules

All skills are available standalone and unchanged.
