# Interactive vs Non-Interactive Modes

**CRITICAL DISTINCTION**: These are two completely separate workflows with different entry points, behaviors, and use cases.

---

## Interactive Mode (Slash Command)

**Entry Point**: `/auto-cdq discovery` or `/auto-cdq onboarding` or `/auto-cdq rules`

**Purpose**: User-guided, exploratory, learning-friendly, **human-controlled pacing**

### Characteristics

| Aspect | Interactive |
|--------|-------------|
| **Entry** | Slash command: `/auto-cdq discovery` |
| **Flow** | Multi-section headers + AskUserQuestion + skills + validation loops |
| **Execution** | Skills run BETWEEN questions (not all at once) |
| **Pacing** | User controls speed - can pause, modify, retry anytime |
| **Validation** | Loops throughout - "More rows?", "Different table?", "Modify?" |
| **Display** | Raw data output (SQL, tables, metrics) shown after each skill |
| **User Control** | Full - can go back, explore alternatives |
| **Error Handling** | Graceful with fallback options |
| **Duration** | Variable (user-paced, 10-60 minutes) |
| **Target User** | Data analysts, business users learning DQ |

### Example Flow

```
1. Question: "Which schema?"
   → User selects "samples"
   → Header updates: ✓ Schema | ☐ Table | ☐ Preview | ☐ Confirm

2. Skill: /cdq-list-tables --schema samples
   → Display: 50 tables in list format
   → Question: "Which table?"
   → User searches, finds "census_tracts_new_york"
   → Header updates: ✓ Schema | ✓ Table | ☐ Preview | ☐ Confirm

3. Skill: /cdq-run-sql --sql "SELECT * FROM census_tracts_new_york LIMIT 5"
   → Display: 5 rows with schema
   → Question: "Looks good?"
   → User says "Yes" or "Show more"
   → [If "Show more": Loop → re-run with LIMIT 20]
   → Header updates: ✓ Schema | ✓ Table | ✓ Preview | ☐ Confirm

4. Question: "Ready to proceed?"
   → User confirms
   → Header updates: ✓ Schema | ✓ Table | ✓ Preview | ✓ Confirm
```

### When to Use

- ✅ New datasets (user needs to explore)
- ✅ Learning (user needs explanation)
- ✅ Validation (user must review output)
- ✅ Configuration (user preferences matter)
- ✅ Investigation (user wants to explore alternatives)

### Example Success Metrics

**2026-04-09 Census Workflow**:
- Discovery: 4 phases, 1 validation loop (show more rows)
- Onboarding: 4 phases, 2 skills, 100% score
- Rules: 4 phases, 13 rules, 18 anomalies detected
- Total: 8 AskUserQuestion prompts, 16+ skill executions
- Duration: ~30 minutes (user-paced)

---

## Non-Interactive Mode (Direct CLI)

**Entry Point**: `python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples --table accounts`

**Purpose**: Headless automation, scripting, batch processing, **unattended execution**

### Characteristics

| Aspect | Non-Interactive |
|--------|---|
| **Entry** | Direct Python script: `python3 .claude/bin/auto-cdq-wizard.py` |
| **Flow** | CLI arguments only, full checklist execution |
| **Execution** | All skills run sequentially with configured parameters |
| **Pacing** | Fast, uninterrupted |
| **Validation** | None - executes full workflow |
| **Display** | Minimal, structured output only (JSON/CSV) |
| **User Control** | None - must specify all params upfront |
| **Error Handling** | Fail-fast (no retry options) |
| **Duration** | Fast (5-15 minutes) |
| **Target User** | DevOps, automation, CI/CD pipelines |

### Example Flow

```
$ python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples --table census_tracts_new_york --limit 10000

[No prompts or questions]
→ Auto-select schema: samples
→ Auto-select table: census_tracts_new_york
→ Auto-run /cdq-list-tables
→ Auto-run /cdq-run-sql (preview)
→ Auto-confirm (no validation)

Output (structured):
{
  "schema": "samples",
  "table": "census_tracts_new_york",
  "rows": 4918,
  "columns": 13,
  "status": "success"
}
```

### When to Use

- ✅ Batch processing (100+ datasets)
- ✅ CI/CD pipelines (automated QA)
- ✅ Scheduled jobs (nightly onboarding)
- ✅ Headless servers (no terminal)
- ✅ Script automation (Airflow, GitLab CI, etc.)

---

## Key Rules

### 🚫 NO Slash Command for Non-Interactive

**Wrong**:
```bash
/auto-cdq discovery --headless --schema samples --table accounts
# ❌ NEVER add --headless flag to slash command
```

**Right**:
```bash
python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples --table accounts
# ✅ Use direct Python script for non-interactive
```

### 🚫 NO CLI Arguments for Interactive

**Wrong**:
```bash
/auto-cdq discovery --schema samples --table accounts
# ❌ Slash command should NOT accept CLI arguments
```

**Right**:
```bash
/auto-cdq discovery
# ✅ Slash command opens interactive workflow
```

### Distinguish in Skill Definition

**SKILL.md frontmatter**:
```yaml
interaction: interactive  # ✅ Mark explicitly
mode: user-guided        # ✅ Describe purpose
commands:
  - name: auto-cdq discovery
    description: "Start interactive Discovery - find and preview tables"
```

**README or CLI help**:
```
Interactive workflows: /auto-cdq discovery
Non-interactive: python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples
```

---

## Real-World Example: Same Dataset, Two Approaches

### Interactive: New Dataset Exploration

**Scenario**: "I have a new census dataset. Let me explore it and set up DQ."

```bash
$ /auto-cdq discovery

# Question: "Which schema?"
→ User: "samples"

# Skill: /cdq-list-tables
# Display: 50 tables
# Question: "Which one?"
→ User searches: "census"
# Skill: /cdq-list-tables --search "%census%"
# Display: 50 census tables
# Question: "Which state?"
→ User: "census_tracts_new_york"

# Skill: /cdq-run-sql (preview)
# Display: Schema, 5 rows
# Question: "Looks good?"
→ User: "Show more"
# Skill: /cdq-run-sql (20 rows)
# Display: 20 rows
# Question: "Looks good?"
→ User: "Yes"

# → Proceed to Onboarding
# Question: "Dataset name?"
→ User: "AUTO_CDQ_samples.census_tracts_new_york"
# ... (continue with onboarding)

# Duration: 30 minutes, user explored alternatives
```

### Non-Interactive: Batch Onboarding

**Scenario**: "I have 100 new datasets. Auto-onboard them all with standard rules."

```bash
$ for table in $(python3 scripts/list-new-tables.py); do
    python3 .claude/bin/auto-cdq-wizard.py discovery \
      --schema samples \
      --table $table \
      --limit 50000 | tee "results/$table.json"
  done

# No questions, no pauses
# Output: Structured JSON for each dataset
# Duration: 5 minutes for 100 datasets
# Error handling: Fail-fast, log errors
```

---

## Implementation Checklist

### For Interactive Skills

- [ ] Use `/auto-cdq discovery` style entry point
- [ ] No CLI arguments in slash command
- [ ] Multi-section headers update after each phase
- [ ] AskUserQuestion for lightweight decisions
- [ ] Skills execute between questions (not batched)
- [ ] Raw output displayed before confirmation
- [ ] At least 1 validation loop per workflow
- [ ] Headers use ☐ (pending) and ✓ (complete)
- [ ] User can go back/modify/retry
- [ ] Error messages suggest next steps

### For Non-Interactive Scripts

- [ ] Use `python3 .claude/bin/auto-cdq-wizard.py discovery` style
- [ ] Accept `--schema`, `--table`, `--dataset`, `--limit` args
- [ ] NO AskUserQuestion or interactive prompts
- [ ] Fail-fast with clear error codes
- [ ] Output structured JSON or CSV
- [ ] Log to STDOUT/STDERR appropriately
- [ ] Handle missing args with clear usage message
- [ ] No validation loops (check args upfront)
- [ ] Fast execution (minutes, not 30+ minutes)
- [ ] Document all CLI args in --help

---

## Distinction in Documentation

### SKILL.md (Interactive)
```markdown
# Auto-CDQ — Interactive Guided Workflows

This skill provides guided, exploratory workflows with validation loops.

**Entry**: `/auto-cdq discovery`

For headless/non-interactive workflows:
$ python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples --table accounts
```

### README (Both Modes)
```markdown
## Usage

### Interactive (Guided)
/auto-cdq discovery
→ Schema selection → Table discovery → Preview → Confirm

### Non-Interactive (Automated)
python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples --table accounts
→ Full workflow with sensible defaults
```

### CLI Help (Non-Interactive)
```bash
$ python3 .claude/bin/auto-cdq-wizard.py discovery --help

Usage: auto-cdq-wizard.py discovery [OPTIONS]

Options:
  --schema TEXT     Database schema (required)
  --table TEXT      Table name (required)
  --limit INTEGER   Row limit (default: 50000)
  --help            Show this message
```

---

## Summary

| Feature | Interactive | Non-Interactive |
|---------|---|---|
| **Entry** | Slash command | Direct CLI |
| **User Prompts** | Multiple | None |
| **Validation Loops** | Yes (user-controlled) | No |
| **Duration** | 30+ min (variable) | 5-15 min (fixed) |
| **Error Recovery** | User guided | Fail-fast |
| **Raw Output** | Full display | Structured only |
| **Use Case** | Exploration/Learning | Automation/Batch |
| **Target** | Analysts/Business | DevOps/Scripts |

---

**Pattern**: Interactive = exploratory, user-paced. Non-interactive = automated, fast. Never mix them.
