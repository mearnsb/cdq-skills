# Hybrid Progressive Disclosure Pattern for CDQ Wizards

## Overview

The **Hybrid Progressive Disclosure Pattern** combines the best of two approaches:

1. **Multi-section headers** (visual cohesion, progress tracking)
2. **Interactive skill execution** (real data, validation loops, feedback)

This pattern eliminates the choice between:
- ❌ Clean UX with no interactivity
- ❌ Powerful interactivity with fragmented UX

Instead, it delivers:
- ✅ **Professional wizard UX** with multi-section headers
- ✅ **Real data integration** via skill execution
- ✅ **Validation loops** where users see results before confirming
- ✅ **Flexible steering** - users can modify choices based on data

---

## Pattern Architecture

### Visual Foundation: Multi-Section Headers

The header shows the complete journey at a glance:

```
═══════════════════════════════════════════════════════════════════════════════
☐ Phase 1    ☐ Phase 2    ☐ Phase 3    ☐ Phase 4
═══════════════════════════════════════════════════════════════════════════════
```

As user progresses:

```
═══════════════════════════════════════════════════════════════════════════════
✓ Phase 1    ☐ Phase 2    ☐ Phase 3    ☐ Phase 4
═══════════════════════════════════════════════════════════════════════════════
```

Final state:

```
═══════════════════════════════════════════════════════════════════════════════
✓ Phase 1    ✓ Phase 2    ✓ Phase 3    ✓ Phase 4
═══════════════════════════════════════════════════════════════════════════════
```

### Core Components

#### 1. Lightweight Decisions
- Simple AskUserQuestion calls
- Predefined options
- No skill execution needed
- Example: "Which schema?" or "Yes/No confirmation"

#### 2. Heavy Operations (Skill Execution)
- Run skills between questions
- Display raw output (SQL, results, metrics)
- Show impact to user
- Example: Run `cdq-list-tables`, show results table

#### 3. Validation Loops
- After displaying results, ask for feedback
- Allow user to modify earlier choices
- Can loop: "Show more rows?" → run again → ask again
- Example: Preview data → "Looks good?" → loop if "More rows"

#### 4. Batch Operations
- Group related rules/items
- Test individually
- Ask once for batch confirmation
- Example: Test 10 rules one by one, then ask "Save all?"

---

## Implementation Pattern

### Flow Template

```
┌─ Header printed (all phases as ☐)
│
├─ PHASE 1 (Lightweight)
│  └─ AskUserQuestion → Answer → Mark ✓, Update header
│
├─ PHASE 2 (Interactive)
│  ├─ AskUserQuestion (search term?) → Answer
│  ├─ Run Skill (cdq-list-tables) → Display results
│  ├─ AskUserQuestion (pick from results?) → Answer → Mark ✓
│  └─ Update header
│
├─ PHASE 3 (Validation Loop)
│  ├─ Run Skill (cdq-run-sql) → Display data + SQL
│  ├─ AskUserQuestion (looks good?) → Answer
│  ├─ If No: Loop back (show more/different)
│  ├─ If Yes: Mark ✓
│  └─ Update header
│
├─ PHASE 4 (Batch Operations)
│  ├─ For each item:
│  │  ├─ Run Skill (test/validate)
│  │  ├─ Display result
│  │  └─ Ask keep? (modify/skip/save)
│  ├─ After all: AskUserQuestion (batch confirm?)
│  ├─ Mark ✓
│  └─ Update header
│
└─ Final state: All phases ✓, Execute final action
```

---

## Four Workflow Patterns

### Pattern A: Simple Selection (Low Interaction)

**Use when:** Straightforward choices, no validation needed

```
Header: ☐ Schema    ☐ Table    ☐ Preview    ☐ Confirm

Phase 1: Ask schema → Answer → Mark ✓
Phase 2: Ask table → Answer → Mark ✓
Phase 3: Show preview → Confirm → Mark ✓
Phase 4: Confirm next → Answer → Mark ✓
```

**Minimal skill usage.** Mostly AskUserQuestion flows.

---

### Pattern B: Search + Results (Moderate Interaction)

**Use when:** User searches for something, needs to pick from results

```
Header: ☐ Search Method    ☐ Results    ☐ Selection    ☐ Confirm

Phase 1: Ask search method → Answer → Mark ✓
Phase 2: Ask search term → Run skill → Display results table
Phase 3: Ask pick from results → Answer → Mark ✓
Phase 4: Confirm → Answer → Mark ✓
```

**Skills in middle.** Shows actual data before asking user decision.

---

### Pattern C: Preview + Validation (High Interaction)

**Use when:** User needs to see actual data/output before confirming

```
Header: ☐ Config    ☐ Preview    ☐ Validation    ☐ Confirm

Phase 1: Ask config → Answer → Mark ✓
Phase 2: Run Skill → Display SQL + results table
Phase 3: Ask validation (looks good/more/different?)
       → If more: Loop (run skill again)
       → If different: Back to Phase 1
       → If yes: Mark ✓
Phase 4: Confirm → Answer → Mark ✓
```

**Validation loops.** User can refine multiple times.

---

### Pattern D: Batch Operations (Complex)

**Use when:** Multiple items to test/validate before batch save

```
Header: ☐ Analyze    ☐ Select    ☐ Test Each    ☐ Batch Save

Phase 1: Ask analyze? → Run skill → Display suggestions → Mark ✓
Phase 2: Ask which types? → Answer → Mark ✓
Phase 3: For each item:
         - Run Skill (test)
         - Display result
         - Ask keep/modify/skip?
       → Mark ✓ when all processed
Phase 4: Ask batch save? → Answer → Run save skill → Mark ✓
```

**Most complex.** Individual validation + batch summary.

---

## Implementation Checklist

### Step 1: Define Your Workflow

- [ ] List all phases (3-4 typically)
- [ ] For each phase, identify: lightweight question vs. heavy operation
- [ ] Plan skill execution points
- [ ] Identify validation loops
- [ ] Design headers for each phase

### Step 2: Structure in Code

```python
# Print header
print_header(phases=["Phase 1", "Phase 2", "Phase 3", "Phase 4"])

# Phase 1: Lightweight
answer1 = ask_question_1()
mark_complete("Phase 1")
update_header()

# Phase 2: Interactive with skill
answer2a = ask_search_term()
results = run_skill("search")
print_results(results)
answer2b = ask_pick_from_results(results)
mark_complete("Phase 2")
update_header()

# Phase 3: Validation loop
while not validated:
    result = run_skill("preview")
    print_preview(result)
    feedback = ask_validation_question()
    if feedback == "yes":
        validated = True
        mark_complete("Phase 3")
    elif feedback == "more":
        # Loop: modify params, run again
        pass
    elif feedback == "different":
        # Back to Phase 2
        return to_phase_2()

update_header()

# Phase 4: Final
answer4 = ask_final_confirmation()
mark_complete("Phase 4")
update_header()

# Execute
final_action()
```

### Step 3: Print Helper Functions

```python
def print_header(phase_states):
    """Print multi-section header with checkmarks"""
    header = " ".join([
        f"{'✓' if state == 'complete' else '☐'} {name}"
        for name, state in phase_states.items()
    ])
    print(f"\n{'═' * 80}")
    print(header)
    print(f"{'═' * 80}\n")

def print_results_table(data, columns):
    """Print results in formatted table"""
    # Use markdown table or ASCII art
    pass

def print_sql_query(sql):
    """Print SQL in code block"""
    print(f"┌{'─' * 60}┐")
    print(f"│ {sql:<58} │")
    print(f"└{'─' * 60}┘")
```

### Step 4: AskUserQuestion Integration

```python
response = AskUserQuestion(questions=[
    {
        "question": "Your question?",
        "header": "Phase 1",
        "multiSelect": False,
        "options": [...]
    }
])

# Extract answer
answer = response["Your question?"]
```

### Step 5: Skill Execution Points

```python
# Run skill between questions
result = run_skill(
    "cdq-list-tables",
    args="--schema samples --search customer"
)

# Display results
display_results(result)

# Ask for feedback
confirmation = ask_user_to_pick_from_results(result)
```

### Step 6: Testing

- [ ] Test full flow end-to-end
- [ ] Verify headers update correctly
- [ ] Test all skill execution points
- [ ] Test validation loops (go back, modify, confirm)
- [ ] Test edge cases (no results, errors, etc.)

---

## Best Practices

### Header Management

✅ **DO:**
- Update header after each major phase
- Use consistent formatting
- Show progress visually

❌ **DON'T:**
- Update header for every single step (too noisy)
- Use complex Unicode that won't render
- Show incomplete header (always show all phases)

### Skill Execution

✅ **DO:**
- Run skills between questions (not before)
- Display raw output (SQL, results, stats)
- Show query metadata (rows, columns, processing time)
- Provide context for results

❌ **DON'T:**
- Hide skill execution status
- Show only summary (hide raw data)
- Skip error handling
- Run expensive queries without warning

### Validation Loops

✅ **DO:**
- Show what will happen before asking confirmation
- Allow looping back easily
- Save state so user doesn't lose choices
- Provide clear "Yes/No/Modify" options

❌ **DON'T:**
- Ask confirmation without showing preview
- Make it hard to go back
- Lose state between loops
- Provide vague options ("Continue", "OK")

### User Experience

✅ **DO:**
- Start with recommended defaults
- Explain what each phase does
- Show progress clearly
- Provide clear error messages

❌ **DON'T:**
- Make every option mandatory
- Require expert knowledge
- Hide errors or skip over them
- Overwhelm with too many options per question

---

## Common Workflows

### Discovery Workflow

**Goal:** Find and preview a table

**Phases:**
1. Schema selection (lightweight)
2. Table search (interactive search → results → pick)
3. Preview (validation loop with more rows option)
4. Next action (confirm or move to onboarding)

**Skills used:**
- `cdq-list-tables` (search)
- `cdq-run-sql` (preview with LIMIT)

---

### Onboarding Workflow

**Goal:** Configure dataset and run initial DQ job

**Phases:**
1. Dataset name (lightweight config)
2. Sample size (interactive with row count check)
3. Connection test (validation)
4. Run job (execution + results)

**Skills used:**
- `cdq-run-sql` (row count)
- `cdq-test-connection` (validate)
- `cdq-run-dq-job` (execute)
- `cdq-get-results` (display)

---

### Rules Workflow

**Goal:** Create and validate data quality rules

**Phases:**
1. Analysis (analyze data → suggest rules)
2. Rule selection (pick which rules)
3. Test each (batch operation: test → validate → keep/skip)
4. Save (batch save all validated rules)

**Skills used:**
- `cdq-workflow-suggest-rules` (analysis)
- `cdq-run-sql` (test each rule)
- `cdq-save-rule` (save)

---

### Alerts Workflow

**Goal:** Create alerts for data quality events

**Phases:**
1. Rule selection (pick which rule to alert on)
2. Condition definition (define alert threshold)
3. Recipients (where/who to notify)
4. Test and save (validate condition works)

**Skills used:**
- `cdq-get-rules` (list available rules)
- `cdq-run-sql` (test alert condition)
- `cdq-save-alert` (create alert)

---

## Error Handling

### When Skills Fail

**Option 1: Show error in context**
```
Phase X: [Action description]
🔄 [RUNNING SKILL]
❌ Error: Connection failed
  Message: Unable to reach CDQ API

❓ What would you like to do?
  1. Retry
  2. Go back to previous phase
  3. Exit
```

**Option 2: Provide recovery path**
```
❌ Connection test failed

Header still shows: ✓ Phase 1  ☐ Phase 2  ⚠️ Phase 3 (failed)

Q: Should we:
  1. Retry connection?
  2. Check configuration?
  3. Skip and continue?
```

### When Validation Fails

**Show why, offer fixes:**
```
Test result: 47 records would fail this rule

Q: This rule might be too strict. Would you like to:
  1. Adjust the rule SQL
  2. Keep it as-is (catches real issues)
  3. Skip this rule
```

---

## Performance Considerations

### Skill Execution Time

- **Fast (<1s):** `cdq-list-tables`, `cdq-get-rules`
- **Medium (1-5s):** `cdq-run-sql` with LIMIT, `cdq-test-connection`
- **Slow (5-30s):** `cdq-workflow-suggest-rules`, large `cdq-run-sql`

### Optimization Strategies

1. **Use LIMIT aggressively**
   - Preview: `LIMIT 5`
   - Analysis: `LIMIT 1000`
   - Never: unlimited queries

2. **Show progress**
   - "Fetching table list..." during skill execution
   - "Analyzing 1,000 rows..."
   - "Testing rule against data..."

3. **Cache results**
   - Reuse row count if not changed
   - Don't re-run same query twice
   - Store skill outputs in phase state

---

## Testing Checklist

- [ ] Full workflow end-to-end
- [ ] Each phase independently
- [ ] Header updates correctly
- [ ] Skill execution and error handling
- [ ] Validation loops (test multiple iterations)
- [ ] Going back to previous phases
- [ ] Modifying earlier choices
- [ ] Error cases (no results, API failures)
- [ ] Edge cases (empty results, large results)
- [ ] UX flow (is it clear what to do?)

---

## Migration from Old Pattern

If moving from separate AskUserQuestion calls to this pattern:

### Before (4 separate calls)
```
Q1: Schema → Answer
Q2: Table → Answer
Q3: Preview OK? → Answer
Q4: Next action? → Answer
```

### After (Hybrid with interaction)
```
Q1: Schema → Answer → Mark ✓
    Run: cdq-list-tables → Display results
Q2: Pick table? → Answer → Mark ✓
    Run: cdq-run-sql → Display preview
Q3: Preview OK? → Answer (with loop option)
Q4: Next action? → Answer → Mark ✓
```

**Key changes:**
1. Don't batch all 4 Qs together (they're sequential, not parallel)
2. Add skill execution **between** questions
3. Add validation **loops** where needed
4. Update header after each section

---

## Real-World Example: Discovery Workflow

See full implementation in: `docs/DISCOVERY_WORKFLOW_EXAMPLE.md`

Demonstrates:
- ✅ Schema selection (lightweight)
- ✅ Table search with results (interactive)
- ✅ Preview with validation loop (high interaction)
- ✅ Next action routing (decision point)

---

## References

- `docs/ONBOARDING_WORKFLOW_EXAMPLE.md` - Onboarding implementation
- `docs/RULES_WORKFLOW_EXAMPLE.md` - Rules implementation
- `docs/ALERTS_WORKFLOW_EXAMPLE.md` - Alerts implementation
- `lib/client.py` - Available skills

