# Auto-CDQ Hybrid Progressive Disclosure Pattern — Complete Implementation

## Status: ✅ Complete

All three CDQ workflows have been successfully implemented using the **hybrid progressive disclosure pattern** with multi-section headers and interactive skill execution.

---

## What's New

### SKILL.md Fully Updated (910 lines)

The `.claude/skills/auto-cdq/SKILL.md` file now contains complete, executable instructions for all three workflows:

1. **Discovery Workflow** — Find and preview tables
2. **Onboarding Workflow** — Register dataset and run DQ job
3. **Rules Workflow** — Analyze data and create quality rules

Each workflow follows the same pattern:
- Multi-section headers tracking progress (☐/✓ checkmarks)
- AskUserQuestion for lightweight user decisions
- Skill execution points with raw output display
- Validation loops allowing user refinement
- Progressive disclosure of complexity

---

## How to Use

### Available Commands

```bash
/auto-cdq                # Show workflow selection menu
/auto-cdq discovery      # Jump straight to Discovery Workflow
/auto-cdq onboarding     # Jump straight to Onboarding Workflow
/auto-cdq rules          # Jump straight to Rules Workflow
```

### Example: Discovery Workflow

Running `/auto-cdq discovery` will:

1. **Display header with all phases**
   ```
   ═══════════════════════════════════════════════════════════════════════════════
   ☐ Schema      ☐ Table       ☐ Preview     ☐ Confirm
   ═══════════════════════════════════════════════════════════════════════════════
   ```

2. **Phase 1: Schema Selection**
   - Ask: "Which schema should we search in?"
   - Update header: ✓ Schema (mark complete)

3. **Phase 2: Table Discovery**
   - Run: `/cdq-list-tables --schema {schema}`
   - Display results table
   - Ask: "Which table would you like to work with?"
   - Update header: ✓ Table

4. **Phase 3: Data Preview**
   - Run: `/cdq-run-sql --sql "SELECT * FROM {schema}.{table} LIMIT 5"`
   - Display SQL query and results
   - Ask: "Preview looks good?" (with options: Yes / Show more / Choose different)
   - Allow loops: User can ask for more rows without re-doing earlier steps
   - Update header: ✓ Preview

5. **Phase 4: Confirmation**
   - Ask: "Ready to proceed?"
   - Update header: ✓ Confirm
   - Show completion summary

---

## Pattern Architecture

### Core Components

Each workflow contains:

1. **Multi-Section Headers**
   - Visual progress tracking with ☐ (pending) and ✓ (complete)
   - Updated after each major phase
   - Shows the entire journey at a glance

2. **Lightweight Questions**
   - AskUserQuestion calls with predefined options
   - No skill execution needed
   - Examples: "Which schema?", "Yes/No?", "Do you want X?"

3. **Heavy Operations (Skill Execution)**
   - Run CDQ skills between questions
   - Display raw output (SQL queries, result tables, statistics)
   - Show query metadata (rows, columns, processing time)

4. **Validation Loops**
   - After displaying results, ask for user feedback
   - Allow user to modify earlier choices
   - Example: "Show more rows?" → run again → ask again
   - No need to restart from the beginning

5. **Batch Operations** (Rules Workflow)
   - Test multiple items individually
   - Show results for each
   - Ask once for batch confirmation
   - Then save all together

---

## Discovery Workflow Details

### Four Phases

**Phase 1: Schema Selection** (Lightweight)
- Ask user which schema to search in
- Options: samples, custom schema, or chat
- Mark complete: ✓ Schema

**Phase 2: Table Discovery** (Interactive)
- Ask how to find tables: search/browse/direct entry
- Run `/cdq-list-tables` skill
- Display available tables
- Ask user to pick from results
- Mark complete: ✓ Table

**Phase 3: Data Preview** (Validation Loop)
- Run `/cdq-run-sql` to get sample data
- Display SQL query and result table
- Ask if preview looks good
- Options: Yes / Show more rows / Choose different table / Chat
- If "Show more": Re-run with LIMIT 20, ask again (loop)
- If "Choose different": Back to Phase 2
- Mark complete: ✓ Preview

**Phase 4: Confirmation** (Lightweight)
- Ask: Ready to proceed?
- Mark complete: ✓ Confirm
- Show final summary

---

## Onboarding Workflow Details

### Four Phases

**Phase 1: Data Source Selection** (Interactive)
- If discovery was done: Offer to reuse
- If new: Run mini-discovery (Phases 1-3)
- Mark complete: ✓ Data Source

**Phase 2: Dataset Configuration** (Lightweight)
- Ask dataset name (suggest: `{table}_dq`)
- Ask row limit (10K/50K/100K/Full)
- Mark complete: ✓ Config

**Phase 3: Validation** (Interactive)
- Run `/cdq-test-connection` to verify API access
- Run `/cdq-run-sql` to get actual row count
- Display: Total rows available, processing estimate
- Ask: Ready to proceed?
- Mark complete: ✓ Validation

**Phase 4: Execute & Results** (Skill Execution)
- Run `/cdq-run-dq-job` to register and execute
- Run `/cdq-get-results` to retrieve quality score
- Display: Job ID, status, DQ score, quality breakdown
- Mark complete: ✓ Execute
- Ask: Next action? (Create rules / Set alerts / Exit)

---

## Rules Workflow Details

### Four Phases

**Phase 1: Dataset Selection** (Lightweight)
- Ask which dataset to create rules for
- Options: Recent onboarding, search catalog, custom
- Mark complete: ✓ Dataset

**Phase 2: Data Analysis** (Interactive)
- Run `/cdq-workflow-suggest-rules` to analyze
- Display suggested rules table (priority, type, impact)
- Shows: 4 HIGH, 3 MEDIUM, 5 LOW (example)
- Mark complete: ✓ Analysis

**Phase 3: Rule Selection** (Lightweight)
- Ask which rules to create (multi-select)
- Options grouped by priority
- Examples: "[HIGH] name_not_null", "[MEDIUM] date_format"
- Mark complete: ✓ Select

**Phase 4: Test & Save** (Complex Batch)
- For each selected rule:
  - Display rule name and SQL
  - Run `/cdq-run-sql` to test
  - Show violations count
- Ask: Ready to save all?
- For each approved rule:
  - Run `/cdq-save-rule`
- Show completion summary
- Mark complete: ✓ Test & Save
- Ask: Next action? (Run job / Create alerts / Exit)

---

## Why It's "Hybrid"

The pattern is called "hybrid" because it combines:

1. **Claude Code layer** (UI/orchestration)
   - AskUserQuestion for user interactions
   - Multi-section headers for visual feedback
   - Skill routing and flow control

2. **CDQ Skills layer** (data/backend)
   - `/cdq-list-tables` — Database queries
   - `/cdq-run-sql` — Data preview
   - `/cdq-run-dq-job` — Job execution
   - All existing skills work standalone

Result: Professional wizard UX with real data feedback

---

## Implementation Files

### Main File
- **`.claude/skills/auto-cdq/SKILL.md`** (910 lines)
  - Frontmatter with command definitions
  - Discovery workflow (4 phases, 145 lines)
  - Onboarding workflow (4 phases, 215 lines)
  - Rules workflow (4 phases, 235 lines)
  - Pattern architecture documentation
  - Helper code patterns (Python examples)

### Supporting Documentation
- `docs/HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md` — Pattern theory
- `docs/DISCOVERY_WORKFLOW_EXAMPLE.md` — Complete Discovery example
- `docs/ONBOARDING_WORKFLOW_EXAMPLE.md` — Complete Onboarding example
- `docs/RULES_WORKFLOW_EXAMPLE.md` — Complete Rules example
- `docs/ALERTS_WORKFLOW_EXAMPLE.md` — Alert workflow template

### State Management (Optional)
- `.auto-cdq-state.json` — Persists workflow progress (for future enhancements)

---

## All CDQ Skills Remain Unchanged

The implementation doesn't touch any existing skills. Users can still:

```bash
/cdq-list-tables           # Use directly
/cdq-run-sql               # Use directly
/cdq-run-dq-job            # Use directly
/cdq-save-rule             # Use directly
...and all others          # Still work standalone
```

Plus they can now use the guided workflows:

```bash
/auto-cdq discovery        # Guided experience
/auto-cdq onboarding       # Guided experience
/auto-cdq rules            # Guided experience
```

---

## Testing the Implementation

### Quick Test: Discovery Workflow

```
Run: /auto-cdq discovery

Expected flow:
1. Shows header with 4 phases (all ☐)
2. Asks: "Which schema?"
3. Updates header: ✓ Schema  ☐ Table  ☐ Preview  ☐ Confirm
4. Asks: "Browse tables or search?"
5. Runs: /cdq-list-tables (displays results)
6. Asks: "Pick a table?"
7. Updates header: ✓ Schema  ✓ Table  ☐ Preview  ☐ Confirm
8. Runs: /cdq-run-sql (displays data preview)
9. Asks: "Looks good?" (with "Show more" option)
10. Updates header: ✓ Schema  ✓ Table  ✓ Preview  ☐ Confirm
11. Asks: "Ready to proceed?"
12. Updates header: ✓ Schema  ✓ Table  ✓ Preview  ✓ Confirm
13. Shows completion summary
```

---

## Next Steps

The implementation is complete and ready to use. Future enhancements could include:

- **Alerts Workflow** — Create alerts for rules (template in docs already)
- **Monitoring Workflow** — Track rule performance over time
- **Batch Operations** — Process multiple datasets
- **Scheduling** — Set up recurring DQ jobs
- **State Persistence** — Support mid-session resume (`.auto-cdq-state.json`)

All follow the same hybrid pattern documented here.

---

## Quick Reference

| Command | Purpose | Phases |
|---------|---------|--------|
| `/auto-cdq` | Show menu | Menu selection |
| `/auto-cdq discovery` | Find & preview tables | Schema → Table → Preview → Confirm |
| `/auto-cdq onboarding` | Register & run DQ job | Data Source → Config → Validation → Execute |
| `/auto-cdq rules` | Create quality rules | Dataset → Analysis → Select → Test & Save |

---

**Created**: April 9, 2025
**Status**: Production Ready ✅
**All Skills**: Unchanged ✅
**Pattern**: Hybrid Progressive Disclosure ✅
