# Auto-CDQ Wizard — Complete Implementation ✅

## What Is This?

A **standalone orchestrator** that provides an interactive `/auto-cdq` command to guide users through Collibra DQ workflows (Discovery, Onboarding, Rules).

**Key feature**: All existing CDQ skills remain **completely unchanged** and available as standalone commands.

---

## Quick Start (1 minute)

```bash
# Show workflow menu
/auto-cdq

# Or jump directly to a workflow
/auto-cdq discovery      # Find and preview tables
/auto-cdq onboarding     # Register dataset and run job
/auto-cdq rules          # Create quality rules
```

For details, see **[AUTO_CDQ_QUICK_START.md](AUTO_CDQ_QUICK_START.md)**.

---

## How It Works (Architecture)

```
User: /auto-cdq discovery
         ↓
.claude/skills/auto-cdq/SKILL.md (tells Claude Code to run wrapper)
         ↓
.claude/bin/auto-cdq-wizard.py (orchestrator script)
         ├→ Calls /cdq-list-tables (existing skill, unchanged)
         ├→ Calls /cdq-run-sql (existing skill, unchanged)
         ├→ Calls /cdq-run-dq-job (existing skill, unchanged)
         └→ ... all 15+ skills unchanged
         ↓
State saved to .auto-cdq-state.json
```

**Benefits**:
- ✅ Wrapper is isolated in `.claude/bin/`
- ✅ All public-repo skills unchanged
- ✅ Individual skills still work standalone (/cdq-search-catalog, /cdq-run-sql, etc.)
- ✅ Easy to iterate on wizard UX
- ✅ No breaking changes

---

## What's Included

### 1. Wrapper Orchestrator
**File**: `.claude/bin/auto-cdq-wizard.py` (395 lines)

**Implements**:
- Entry point for `/auto-cdq` command
- Three complete workflows:
  - **Discovery** — Find and preview tables
  - **Onboarding** — Register dataset and run DQ job
  - **Rules** — Analyze data and create quality rules
- State management (`.auto-cdq-state.json`)
- Backward navigation support

**Status**: ✅ Syntax-validated, ready to use

### 2. Skill Definition
**File**: `.claude/skills/auto-cdq/SKILL.md` (180 lines)

**Simplified from 897 lines to 180 lines**:
- Removed verbose implementation specs
- Added clean, user-focused documentation
- Clearly documents the orchestrator architecture
- References the wrapper script

**Status**: ✅ Updated and focused

### 3. Documentation
- **[AUTO_CDQ_QUICK_START.md](AUTO_CDQ_QUICK_START.md)** — Get started quickly (5 min read)
- **[AUTO_CDQ_WRAPPER_IMPLEMENTATION.md](AUTO_CDQ_WRAPPER_IMPLEMENTATION.md)** — Deep technical details

---

## Three Workflows

### 🔍 Discovery Workflow
Guide through table discovery:

```
1. Select schema        (or use configured default)
2. Find table           (search or browse)
3. Preview data         (5 rows with columns)
4. Choose next step     (Onboarding, Rules, or continue)
```

**Calls**: `/cdq-list-tables`, `/cdq-run-sql`

### 📝 Onboarding Workflow
Register dataset and run DQ job:

```
1. Configure dataset name    (suggested: {table}_dq)
2. Choose data size          (1K, 10K, 50K, 100K, or full)
3. Test connection           (verify CDQ API access)
4. Run DQ job                (execute with chosen limit)
5. View results              (show DQ score and findings)
```

**Calls**: `/cdq-test-connection`, `/cdq-run-dq-job`, `/cdq-get-results`

### ✅ Rules Workflow
Analyze data and create quality rules:

```
1. Analyze dataset           (find patterns for rules)
2. Select rules              (choose HIGH/MEDIUM/LOW priority)
3. Test rules                (see how many rows each flags)
4. Save rules                (create in dataset)
```

**Calls**: `/cdq-workflow-suggest-rules`, `/cdq-run-sql`, `/cdq-save-rule`

---

## State Management

**File**: `.auto-cdq-state.json` (created at runtime)

**Persists**:
- Workflow name (discovery, onboarding, or rules)
- Schema and table selections
- Dataset name and configuration
- Rules selected and tested
- Backward navigation history

**Enables**:
- Continue sessions across restarts
- Modify earlier choices without restarting
- Pre-fill fields when revisiting

**Clear**: Delete the file or complete workflow to start fresh

---

## All Existing Skills Remain Unchanged

The following 15+ skills work exactly as before (unchanged):

- `/cdq-search-catalog` — Search registered datasets
- `/cdq-list-tables` — List tables in a database
- `/cdq-run-sql` — Execute SQL queries directly
- `/cdq-run-dq-job` — Register dataset and run job
- `/cdq-save-rule` — Create new data quality rules
- `/cdq-get-results` — Retrieve DQ job results
- `/cdq-get-rules` — Get existing rules
- `/cdq-test-connection` — Test API connection
- `/cdq-get-alerts` — View alerts
- `/cdq-save-alert` — Create alerts
- `/cdq-get-dataset` — Get dataset configuration
- `/cdq-get-jobs` — List queued/running jobs
- `/cdq-get-recent-runs` — Get recent job runs
- `/cdq-workflow-suggest-rules` — Suggest rules from data analysis
- `/cdq-workflow-explore-dataset` — Complete exploration workflow
- `/cdq-workflow-run-complete-job` — Complete job workflow

**No changes** to any of these skills. They all work standalone.

---

## Files & Structure

```
.claude/
  ├─ bin/
  │  └─ auto-cdq-wizard.py      (NEW: orchestrator script)
  └─ skills/
     └─ auto-cdq/
        ├─ SKILL.md             (UPDATED: simplified docs)
        ├─ lib/
        │  └─ client.py         (unchanged)
        └─ SKILL.md.backup.v1   (backup from before)

.auto-cdq-state.json            (created at runtime)

AUTO_CDQ_README.md              (this file)
AUTO_CDQ_QUICK_START.md         (user quick start)
AUTO_CDQ_WRAPPER_IMPLEMENTATION.md  (technical details)
```

---

## Usage Examples

### Show workflow menu
```bash
/auto-cdq
```

Output:
```
AUTO-CDQ WIZARD: Workflow Selection
================================================================

1) Discovery (Recommended)     — Find and preview tables
2) Onboarding                   — Register dataset and run job
3) Rules                        — Analyze data and create rules
4) Exit                         — Finish the session

Choose an option (1-4):
→ _
```

### Jump to specific workflow
```bash
/auto-cdq discovery      # Start table discovery
/auto-cdq onboarding     # Skip to dataset registration
/auto-cdq rules          # Jump to rule creation
```

### Use individual skills (unchanged)
```bash
/cdq-list-tables --schema samples
/cdq-run-sql --sql "SELECT * FROM samples.customers LIMIT 5"
/cdq-run-dq-job --dataset my_dataset --sql "..."
/cdq-save-rule --dataset my_dataset --name "my_rule" --sql "..."
```

---

## Troubleshooting

### Connection Issues
If the wizard can't reach CDQ:
1. The wizard will run `/cdq-test-connection`
2. Check `.env` or `.claude/settings.local.json` for credentials
3. Verify network connectivity to CDQ server

### No Tables Found
If search returns 0 results:
1. Try a different schema
2. Verify table exists in your datasource
3. Run `/cdq-list-tables --schema <name>` to debug

### SQL Errors
If preview or job fails:
1. Error message shows the problematic query
2. Try `/cdq-run-sql --sql "..."` directly to test
3. Modify schema/table selection and retry

---

## Architecture Pattern

This is a **clean separation of concerns**:

| Component | Location | Responsibility |
|-----------|----------|-----------------|
| Wizard UX | `.claude/bin/auto-cdq-wizard.py` | Menus, state, workflows |
| Skill Def | `.claude/skills/auto-cdq/SKILL.md` | Entry point, docs |
| CDQ Ops | `.claude/skills/cdq-*/SKILL.md` | Data operations |

**Result**:
- Wrapper can be updated without touching existing skills
- Existing skills can be used standalone
- Public repo deployment ready
- No breaking changes

---

## Next Steps

1. **Try it out**:
   ```bash
   /auto-cdq discovery
   ```

2. **Read the guides**:
   - [AUTO_CDQ_QUICK_START.md](AUTO_CDQ_QUICK_START.md) — 5-minute overview
   - [AUTO_CDQ_WRAPPER_IMPLEMENTATION.md](AUTO_CDQ_WRAPPER_IMPLEMENTATION.md) — Full details

3. **Use standalone skills** as before:
   ```bash
   /cdq-run-sql --sql "SELECT * FROM table LIMIT 5"
   ```

---

## Testing Checklist

Before production use:

- [ ] `/auto-cdq` shows menu
- [ ] `/auto-cdq discovery` enters discovery workflow
- [ ] Schema/table selection works
- [ ] Data preview displays correctly
- [ ] Can proceed to Onboarding or Rules
- [ ] Onboarding: dataset registration and job execution work
- [ ] Rules: suggestion, testing, and saving work
- [ ] State file persists progress
- [ ] Backward navigation via state works
- [ ] Existing skills still work (`/cdq-run-sql`, etc.)

---

## Status

✅ **Implementation Complete**

- [x] Wrapper orchestrator created
- [x] Skill definition updated
- [x] Three workflows implemented
- [x] State management ready
- [x] Documentation complete
- [x] Syntax validated
- [x] All existing skills unchanged

**Ready to use**: `/auto-cdq`

---

## Support

For detailed technical information:
- See [AUTO_CDQ_WRAPPER_IMPLEMENTATION.md](AUTO_CDQ_WRAPPER_IMPLEMENTATION.md)

For quick usage reference:
- See [AUTO_CDQ_QUICK_START.md](AUTO_CDQ_QUICK_START.md)

For skill documentation:
- See `.claude/skills/auto-cdq/SKILL.md`

---

**Last Updated**: 2026-04-09
