# Quick Reference: Interactive Workflow Pattern

**For**: Creating new interactive `/auto-cdq-*` style workflows that match the successful 2026-04-09 pattern.

---

## The Pattern (4-Phase Template)

```
═══════════════════════════════════════════════════════════════════════════════
☐ Phase1    ☐ Phase2    ☐ Phase3    ☐ Phase4
═══════════════════════════════════════════════════════════════════════════════

## Phase 1: [Decision Name]

**Header Update**: ✓ Phase1 | ☐ Phase2 | ☐ Phase3 | ☐ Phase4

AskUserQuestion:
  question: "What do you want to do?"
  options: ["Option A (Recommended)", "Option B", "Other"]

Result: Store user selection, proceed to Phase 2

---

## Phase 2: [Data Gathering]

**Header Update**: ✓ Phase1 | ✓ Phase2 | ☐ Phase3 | ☐ Phase4

Skill: /skill-name --arg "value"
Display: Raw output (tables, stats, metrics)

AskUserQuestion:
  question: "Does this look right?"
  options: ["Yes, proceed", "Show more data", "Try different", "Back"]

If loop (Show more/Try different):
  → Re-run skill with different params
  → Display results again
  → Ask again

---

## Phase 3: [Validation]

**Header Update**: ✓ Phase1 | ✓ Phase2 | ✓ Phase3 | ☐ Phase4

For batch operations (like rules):
  FOR EACH item:
    - Skill: Test/validate item
    - Display: Results (violations, issues)
    - Store: For batch operation

AskUserQuestion:
  question: "Ready to save?"
  options: ["Yes, save all", "Modify first", "Cancel"]

---

## Phase 4: [Execution & Results]

**Header Update**: ✓ Phase1 | ✓ Phase2 | ✓ Phase3 | ✓ Phase4

Skill: /final-skill
Display: Comprehensive results (scores, summaries, metrics)

Final Success Message:
```
═══════════════════════════════════════════════════════════════════════════════
✓ Phase1    ✓ Phase2    ✓ Phase3    ✓ Phase4
═══════════════════════════════════════════════════════════════════════════════

🎉 WORKFLOW COMPLETE

[Summary stats]
[Next steps]
```
```

---

## Key Rules

### ✅ DO

1. **Print header at start with all ☐**
2. **Ask one lightweight question** (not a survey)
3. **Execute skill BETWEEN questions**
4. **Display raw output** (SQL, tables, not summaries)
5. **Ask for validation** ("Looks good?")
6. **Provide loop options** ("More?", "Different?", "Back?")
7. **Update header** after each phase (☐ → ✓)
8. **Test each item** before batch saving

### ❌ DON'T

1. Ask all config questions upfront
2. Hide data output
3. Force linear flow (no loops)
4. Use heavy surveys (5+ options)
5. Skip validation before saving
6. Leave header stale
7. Assume all users want same options
8. Leave user confused about where they are

---

## Pattern in Code

### Using AskUserQuestion

```python
# DO: ONE lightweight question with clear options
AskUserQuestion:
  question: "Which schema?"
  header: "Schema"
  multiSelect: false
  options:
    - label: "samples (Recommended)"
      description: "Demo data"
    - label: "Type something else"
      description: "Custom schema"

# DON'T: Heavy survey with many questions
AskUserQuestion:
  question: "Configure your dataset. (1) Name, (2) Row limit, (3) Connection?"
  options: [...]
```

### Using Header Updates

```
START:    ☐ Phase1 | ☐ Phase2 | ☐ Phase3 | ☐ Phase4
Phase 1:  ✓ Phase1 | ☐ Phase2 | ☐ Phase3 | ☐ Phase4
Phase 2:  ✓ Phase1 | ✓ Phase2 | ☐ Phase3 | ☐ Phase4
Phase 3:  ✓ Phase1 | ✓ Phase2 | ✓ Phase3 | ☐ Phase4
DONE:     ✓ Phase1 | ✓ Phase2 | ✓ Phase3 | ✓ Phase4
```

### Using Skill Execution

```
🔄 [RUNNING SKILL: skill-name --arg value]

[Raw output / Table / Results]

AskUserQuestion:  "Does this look good?"
```

---

## Loop Pattern

```
Question → Skill → Display → Validate
                      ↓
                   Loop? → Ask again
                   ↓         ↓
                More/Back   Yes/No
                   ↓
                Re-run skill
                   ↓
                Display again
                   ↓
                Ask validation again
```

---

## Batch Operation Pattern

```
Propose 10 rules

FOR rule_1 to rule_10:
  TEST rule → Display violations → STORE results

Show summary:
  Rule 1: 10 violations
  Rule 2: 0 violations
  ...

Ask: "Save all?"
  → YES: Save all 10
  → MODIFY: Let user pick subset
  → CANCEL: Exit

Display: "Saved 10 rules"
```

---

## Real Example: Discovery Workflow

```
═══════════════════════════════════════════════════════════════════════════════
☐ Schema | ☐ Table | ☐ Preview | ☐ Confirm
═══════════════════════════════════════════════════════════════════════════════

## Phase 1: Schema Selection
AskUserQuestion: "Which schema?"
→ User: "samples"
Header now: ✓ Schema | ☐ Table | ☐ Preview | ☐ Confirm

## Phase 2: Table Discovery
Skill: /cdq-list-tables --schema samples
Display: [TABLE LIST]
AskUserQuestion: "Which table?"
→ User: "Browse" or "Search"
[If search]
  Skill: /cdq-list-tables --schema samples --search "%census%"
  Display: [FILTERED LIST]
  AskUserQuestion: "Now which?"
→ User: "census_tracts_new_york"
Header now: ✓ Schema | ✓ Table | ☐ Preview | ☐ Confirm

## Phase 3: Data Preview
Skill: /cdq-run-sql --sql "SELECT * FROM ... LIMIT 5"
Display: [5 ROWS, SCHEMA, STATS]
AskUserQuestion: "Looks good?"
  Options: ["Yes", "Show more", "Different table"]
[If "Show more"]
  Skill: /cdq-run-sql ... LIMIT 20
  Display: [20 ROWS]
  AskUserQuestion: "Now OK?"
  → User "Yes"
Header now: ✓ Schema | ✓ Table | ✓ Preview | ☐ Confirm

## Phase 4: Confirmation
AskUserQuestion: "Ready to proceed?"
→ User: "Yes"
Header now: ✓ Schema | ✓ Table | ✓ Preview | ✓ Confirm

═══════════════════════════════════════════════════════════════════════════════
✓ DISCOVERY COMPLETE
  Schema: samples
  Table: census_tracts_new_york
  Rows: 4,918
═══════════════════════════════════════════════════════════════════════════════
```

---

## Validation Loop Example (Rules Phase)

```
Test Rule 1: geo_id_uniqueness
Skill: SQL test
Display:
  Violations: 0
  Pass rate: 100%
AskUserQuestion: "Save?"
→ Yes

Test Rule 2: area_land_positive
Skill: SQL test
Display:
  Violations: 18
  Samples: [row 42, row 178, ...]
AskUserQuestion: "Save?"
→ Yes (user may adjust later)

Test Rule 3...

Final AskUserQuestion: "Save all 13 tested rules?"
→ Yes: Save all
→ Modify: User picks subset
→ Cancel: Exit

Skill: Batch save all approved
Display: ✓ Rule 1 saved, ✓ Rule 2 saved, ...
```

---

## Testing Checklist

- [ ] Does header update after each phase?
- [ ] Can user loop in at least one phase?
- [ ] Is raw data displayed before asking confirmation?
- [ ] Are questions lightweight (<5 options)?
- [ ] Can user go back or modify?
- [ ] Are all skills executed between major questions?
- [ ] Does success message show comprehensive results?
- [ ] Are error cases handled gracefully?

---

## Documentation References

- **Full Reference**: `docs/INTERACTIVE_WORKFLOW_REFERENCE.md` (2026-04-09 example)
- **Mode Distinction**: `docs/INTERACTIVE_VS_NONINTERACTIVE.md` (when to use each)
- **Pattern Guide**: `docs/HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md` (deep dive)
- **Skill Definition**: `.claude/skills/auto-cdq/SKILL.md` (live implementation)

---

**Use this template for all new interactive CDQ workflows. The pattern works.**
