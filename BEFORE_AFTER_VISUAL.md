# Multi-Section Headers: Before & After Visual Guide

---

## Discovery Workflow

### BEFORE: Sequential Questions (4 separate calls)

```
┌─────────────────────────────────────────────────┐
│ AUTO-CDQ WIZARD - Discovery Workflow            │
└─────────────────────────────────────────────────┘

QUESTION 1:
┌─────────────────────────────────────────────────┐
│ ☐ Schema                                         │
│                                                  │
│ Which schema should we search in?               │
│                                                  │
│ ❯ 1. samples (Recommended)                      │
│   2. Type something else                        │
│   3. Chat about this                            │
└─────────────────────────────────────────────────┘
[User selects → Answer received]

QUESTION 2 (separate, user has no context):
┌─────────────────────────────────────────────────┐
│ ☐ Table                                          │
│                                                  │
│ Which table would you like to work with?        │
│                                                  │
│ ❯ 1. customers (Recommended)                    │
│   2. Search by pattern                          │
│   3. Browse all tables                          │
│   4. Type something else                        │
└─────────────────────────────────────────────────┘
[User selects → Answer received]

QUESTION 3 (separate, user can't easily go back):
┌─────────────────────────────────────────────────┐
│ ☐ Preview                                        │
│                                                  │
│ Preview of `samples.customers` looks correct?   │
│                                                  │
│ ❯ 1. Yes, use this table (Recommended)          │
│   2. Preview more rows                          │
│   3. Choose different table                     │
└─────────────────────────────────────────────────┘
[User selects → Answer received]

QUESTION 4 (separate, another page):
┌─────────────────────────────────────────────────┐
│ ☐ Next Step                                      │
│                                                  │
│ What would you like to do next?                 │
│                                                  │
│ ❯ 1. Start onboarding (Recommended)             │
│   2. Create data quality rules                  │
│   3. Preview another table                      │
│   4. Exit                                       │
└─────────────────────────────────────────────────┘
[User selects → Answer received]

PROBLEM: User can't see the journey visually
         Backward navigation is hard to implement
         Feels like 4 separate form pages
```

---

### AFTER: Multi-Section Headers (1 batched call)

```
┌────────────────────────────────────────────────────────────────┐
│ AUTO-CDQ WIZARD - Discovery Workflow (IMPROVED)                │
└────────────────────────────────────────────────────────────────┘

INITIAL STATE - All 4 sections visible:
╔════════════════════════════════════════════════════════════════╗
║ ☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step              ║
╚════════════════════════════════════════════════════════════════╝

Which schema should we search in?

❯ 1. samples (Recommended)
  2. Type something else
  3. Chat about this

[User selects answer 1 and presses Enter/→]

AFTER FIRST ANSWER:
╔════════════════════════════════════════════════════════════════╗
║ ✓ Schema    ☐ Table    ☐ Preview    ☐ Next Step              ║
╚════════════════════════════════════════════════════════════════╝

Which table would you like to work with?

❯ 1. customers (Recommended)
  2. Search by pattern
  3. Browse all tables
  4. Type something else

[User can press → to skip, ← to go back]
[If press ← → goes back to Schema question]

AFTER SECOND ANSWER:
╔════════════════════════════════════════════════════════════════╗
║ ✓ Schema    ✓ Table    ☐ Preview    ☐ Next Step              ║
╚════════════════════════════════════════════════════════════════╝

Preview of `samples.customers` (Columns: id, name, email)
does this look correct?

❯ 1. Yes, use this table (Recommended)
  2. Preview more rows
  3. Choose different table

AFTER THIRD ANSWER:
╔════════════════════════════════════════════════════════════════╗
║ ✓ Schema    ✓ Table    ✓ Preview    ☐ Next Step              ║
╚════════════════════════════════════════════════════════════════╝

What would you like to do next?

❯ 1. Start onboarding (Recommended)
  2. Create data quality rules
  3. Preview another table
  4. Exit

USER PRESSES ← TO GO BACK (backward navigation):
╔════════════════════════════════════════════════════════════════╗
║ ✓ Schema    ✓ Table    ☐ Preview    ☐ Next Step              ║
╚════════════════════════════════════════════════════════════════╝

Preview of `samples.customers` — can modify [previous answer]

❯ 1. Yes, use this table (Recommended) [already checked]
  2. Preview more rows
  3. Choose different table

[User can change answer here, then press → to continue]

BENEFIT: User sees journey upfront (4 sections visible)
         Checkmarks show progress (☐ → ✓)
         Easy backward navigation (← key)
         Still on same form, not 4 separate pages
```

---

## Code Comparison

### BEFORE: 4 Sequential Questions

```python
# Question 1
schema_response = AskUserQuestion(questions=[{
    "question": "Which schema should we search in?",
    "header": "Schema",
    "multiSelect": False,
    "options": [...]
}])
schema = schema_response["Which schema should we search in?"]

# Wait for user answer...

# Question 2
table_response = AskUserQuestion(questions=[{
    "question": "Which table would you like to work with?",
    "header": "Table",
    "multiSelect": False,
    "options": [...]
}])
table = table_response["Which table would you like to work with?"]

# Wait for user answer...

# Question 3
preview_response = AskUserQuestion(questions=[{
    "question": "Preview of `{schema}.{table}` — does this look correct?",
    "header": "Preview",
    "multiSelect": False,
    "options": [...]
}])
preview_action = preview_response["Preview of `{schema}.{table}` — does this look correct?"]

# Wait for user answer...

# Question 4
next_response = AskUserQuestion(questions=[{
    "question": "What would you like to do next?",
    "header": "Next Step",
    "multiSelect": False,
    "options": [...]
}])
next_action = next_response["What would you like to do next?"]

# Finally extract all answers
state = {
    "schema": schema,
    "table": table,
    "preview_action": preview_action,
    "next_action": next_action
}
```

**Problems:**
- 4 separate REST calls
- Each question is independent
- No visual context of journey
- Hard to implement backward nav (← key)
- User sees 4 sequential form pages
- ~80 lines of code for simple workflow

---

### AFTER: 1 Batched Call

```python
# All 4 questions in ONE call
response = AskUserQuestion(questions=[
    {
        "question": "Which schema should we search in?",
        "header": "Schema",
        "multiSelect": False,
        "options": [...]
    },
    {
        "question": "Which table would you like to work with?",
        "header": "Table",
        "multiSelect": False,
        "options": [...]
    },
    {
        "question": "Preview of `{schema}.{table}` — does this look correct?",
        "header": "Preview",
        "multiSelect": False,
        "options": [...]
    },
    {
        "question": "What would you like to do next?",
        "header": "Next Step",
        "multiSelect": False,
        "options": [...]
    }
])

# Extract all answers from ONE response dict
state = {
    "schema": response["Which schema should we search in?"],
    "table": response["Which table would you like to work with?"],
    "preview_action": response["Preview of `{schema}.{table}` — does this look correct?"],
    "next_action": response["What would you like to do next?"]
}
```

**Benefits:**
- 1 REST call (batched)
- All questions related and visible
- Header bar shows progress (☐ → ✓)
- Backward nav (←) supported by CLI
- User sees ONE form with sections
- ~35 lines of code (more concise)
- Natural flow with arrow keys

---

## Workflow Structure Before & After

### BEFORE

```
Discovery:
├─ Phase 1: Schema Selection (1 question)
├─ Phase 2: Table Selection (1 question)
├─ Phase 3: Preview (1 question)
├─ Phase 4: Post-Discovery Menu (1 question)
└─ Result: 4 sequential questions on 4 pages

Onboarding:
├─ Phase 1: Table Selection (3 questions)
├─ Phase 2: Dataset Name (1 question)
├─ Phase 3: Sample Size (1 question)
├─ Phase 4: Validation (1 question)
├─ Phase 5: Execution (run job)
└─ Result: 6 questions across multiple pages

Rules:
├─ Phase 1: Table Selection (3 questions)
├─ Phase 2: Analysis (auto)
├─ Phase 3: Rule Selection (1 question)
├─ Phase 4: Rule Testing (per rule, multiple Qs)
├─ Phase 5: Save Rules (auto)
├─ Phase 6: Post-Rules (1 question)
└─ Result: 6+ questions across multiple pages
```

### AFTER

```
Discovery:
├─ Phase 1: Workflow Selection (1 section, 1 batch)
├─ Phase 2: Table Discovery (4 sections, 1 batch)
│          → Schema | Table | Preview | Next Step
└─ Result: Visually cohesive workflow with checkmarks

Onboarding:
├─ Phase 1: Table Selection (4 sections, 1 batch) [reused]
│          → Schema | Table | Preview | Next Step
├─ Phase 2: Configuration (4 sections, 1 batch)
│          → Dataset Name | Sample Size | Validation | Confirm
└─ Result: 2 phases, natural progression

Rules:
├─ Phase 1: Table Selection (4 sections, 1 batch) [reused]
│          → Schema | Table | Preview | Next Step
├─ Phase 2: Analysis & Rules (4 sections, 1 batch)
│          → Analysis | Selection | Testing | Save
└─ Result: 2 phases, clean workflow
```

---

## Navigation & State Flow

### BEFORE: Linear Only
```
User enters
    ↓
Q1: Schema
    ↓
Q2: Table
    ↓
Q3: Preview
    ↓
Q4: Next Step
    ↓
Can't easily go back without re-asking Q1
```

### AFTER: Bidirectional with Checkmarks
```
User enters
    ↓
Show: ☐ Schema | ☐ Table | ☐ Preview | ☐ Next Step
    ↓
User: Selects answer → checkmark appears ✓
    ↓
User: Presses →     → moves to next section ☐
    ↓
User: Presses ←     → goes back to previous section ☐
    ↓
User: Can modify answer (§ marks stay checked after modification)
    ↓
User: Presses → to continue forward
    ↓
All answers collected and returned as ONE dict
```

---

## Summary: Key Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Calls per workflow** | 4-6+ separate | 1-2 batched | 50-75% fewer calls |
| **Code lines per phase** | 80-100 | 35-50 | 50-60% reduction |
| **User sees sections** | One at a time | All at once | Visual journey |
| **Navigation** | Forward only | Bidirectional (← →) | Full control |
| **Progress tracking** | No visual | ✓ Checkmarks | Clarity |
| **Backward nav** | Very hard | Native support | Easy |
| **State tracking** | Per-question | Per-batch | Simpler logic |

---

## Migration Path

### Step 1: Discovery Workflow (DONE)
- Refactored from 4 questions to 1 batch
- SKILL.md updated with batch pattern

### Step 2: Onboarding Workflow (DONE)
- Refactored from 5+ questions to 2 phases with batches
- SKILL.md updated with configuration batch

### Step 3: Rules Workflow (DONE)
- Refactored from 6+ questions to 2 phases with batches
- SKILL.md updated with analysis batch

### Step 4: Python Implementation (READY)
- QUICK_START_IMPLEMENTATION.md provides copy-paste patterns
- IMPLEMENTATION_CHECKLIST.md provides validation

---

**Result:** A more intuitive, visually clear, and code-efficient auto-cdq wizard experience!
