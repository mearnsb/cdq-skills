# Auto-CDQ Wizard — Quick Start

## One-Minute Overview

The auto-cdq wizard is now ready to use. It guides you through three workflows:

1. **Discovery** — Find and preview tables
2. **Onboarding** — Register dataset and run DQ job
3. **Rules** — Analyze data and create quality rules

All existing CDQ skills remain **completely unchanged** and work as standalone commands.

---

## Get Started

### Option 1: Show the Workflow Menu
```bash
/auto-cdq
```

You'll see:
```
1) Discovery (Recommended)
2) Onboarding
3) Rules
4) Exit
```

Choose 1-4 and follow the guided steps.

### Option 2: Jump Directly to a Workflow
```bash
/auto-cdq discovery      # Start with table discovery
/auto-cdq onboarding     # Skip to dataset registration
/auto-cdq rules          # Jump to rule creation
```

---

## What Happens During Each Workflow

###📊 Discovery
1. Pick a schema (or use default: `samples`)
2. Find a table (search or browse)
3. Preview data (shows 5 rows)
4. Choose next step (Onboarding, Rules, or continue exploring)

**Calls these existing skills**:
- `/cdq-list-tables`
- `/cdq-run-sql`

### 📝 Onboarding
1. Name your dataset (suggested: `customers_dq`)
2. Choose data size (1K, 10K, 50K, 100K, or full)
3. Test connection to CDQ
4. Run the DQ job
5. View results

**Calls these existing skills**:
- `/cdq-test-connection`
- `/cdq-run-dq-job`
- `/cdq-get-results`

### ✅ Rules
1. Analyze data for quality patterns
2. Review suggested rules (HIGH/MEDIUM/LOW priority)
3. Test rules (see how many rows they flag)
4. Save validated rules to your dataset

**Calls these existing skills**:
- `/cdq-workflow-suggest-rules`
- `/cdq-run-sql`
- `/cdq-save-rule`

---

## All Existing Skills Still Work

You can use any CDQ skill directly without the wizard:

```bash
/cdq-search-catalog            # Search datasets
/cdq-list-tables               # List tables
/cdq-run-sql                   # Execute queries
/cdq-run-dq-job                # Run jobs
/cdq-save-rule                 # Create rules
/cdq-get-results               # Check results
... and 10+ more
```

**Nothing has changed** about these skills. They work exactly as before.

---

## State & Memory

The wizard remembers your progress in `.auto-cdq-state.json`:

- Saves your schema, table, dataset name, etc.
- Lets you continue later from where you left off
- Clears when you exit the wizard

You can manually delete this file to start fresh:
```bash
rm .auto-cdq-state.json
```

---

## Architecture

```
Your Command
    ↓
/auto-cdq discovery
    ↓
.claude/bin/auto-cdq-wizard.py (wrapper script)
    ↓
Calls existing CDQ skills internally (/cdq-run-sql, /cdq-run-dq-job, etc.)
    ↓
Shows results and guides to next step
```

- **Wrapper**: `.claude/bin/auto-cdq-wizard.py` (new, independent)
- **Skills**: All in `.claude/skills/cdq-*/` (unchanged)
- **State**: `.auto-cdq-state.json` (persists your session)

---

## Troubleshooting

### Connection errors
If the wizard can't reach CDQ, it will run `/cdq-test-connection` to debug.

**Fix options**:
1. Check `.env` or `.claude/settings.local.json` for CDQ credentials
2. Verify network connectivity to your CDQ server
3. Run `/cdq-test-connection` directly to troubleshoot

### No tables found
If a schema search returns 0 results:
1. Try a different schema name
2. Verify the table exists in your datasource
3. Use `/cdq-list-tables --schema samples` directly to debug

### SQL errors
If preview or job fails, the error will show the problematic query.

**Try**:
- `/cdq-run-sql --sql "SELECT * FROM schema.table LIMIT 5"`
- Verify table name and schema
- Check for connectivity issues

---

## Files

| Path | Purpose | Status |
|------|---------|--------|
| `.claude/bin/auto-cdq-wizard.py` | Wizard orchestrator | New ✅ |
| `.claude/skills/auto-cdq/SKILL.md` | Skill definition (docs) | Updated |
| `.auto-cdq-state.json` | Session state | Created at runtime |
| All other skills (`.claude/skills/cdq-*/*`) | Data operations | Unchanged ✅ |

---

## Full Documentation

For details on architecture, workflows, and implementation, see:
- `AUTO_CDQ_WRAPPER_IMPLEMENTATION.md` — Complete technical overview
- `.claude/skills/auto-cdq/SKILL.md` — Skill documentation

---

## Next: Try It Out

```bash
/auto-cdq discovery
```

You're all set! 🚀
