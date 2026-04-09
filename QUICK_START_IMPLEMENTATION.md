# Quick Start: Implementing Multi-Section Headers for auto-cdq

**TL;DR:** The SKILL.md design is complete. This card shows the exact pattern to code.

---

## The Pattern (Copy-Paste Ready)

### Discovery Phase 2: 4-Section Batch

```python
def discovery_phase_2(state):
    """
    Shows: ☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step
    """
    response = AskUserQuestion(questions=[
        {
            "question": "Which schema should we search in?",
            "header": "Schema",
            "multiSelect": False,
            "options": [
                {"label": f"{DQ_SCHEMA} (Recommended)", "description": "Configured schema"},
                {"label": "samples", "description": "Demo schema"},
                {"label": "Type something else", "description": "Custom schema"},
                {"label": "Chat about this", "description": "Discuss options"}
            ]
        },
        {
            "question": "Which table would you like to work with?",
            "header": "Table",
            "multiSelect": False,
            "options": [
                {"label": "customers (Recommended)", "description": "Common table"},
                {"label": "Search by pattern", "description": "Find by name"},
                {"label": "Browse all tables", "description": "List all"},
                {"label": "Type something else", "description": "Custom table"},
                {"label": "Chat about this", "description": "Discuss"}
            ]
        },
        {
            "question": "Preview of `{schema}.{table}` — does this look correct?",
            "header": "Preview",
            "multiSelect": False,
            "options": [
                {"label": "Yes, use this table (Recommended)", "description": "Proceed"},
                {"label": "Preview more rows", "description": "Show 20 rows"},
                {"label": "Choose different table", "description": "Go back"},
                {"label": "Chat about this", "description": "Discuss"}
            ]
        },
        {
            "question": "What would you like to do next?",
            "header": "Next Step",
            "multiSelect": False,
            "options": [
                {"label": "Start onboarding (Recommended)", "description": "Register dataset"},
                {"label": "Create data quality rules", "description": "Go to rules"},
                {"label": "Preview another table", "description": "Search again"},
                {"label": "Chat about this", "description": "Discuss"},
                {"label": "Exit", "description": "End session"}
            ]
        }
    ])

    # Extract using question text (NOT header)
    schema = response["Which schema should we search in?"]
    table = response["Which table would you like to work with?"]
    preview_action = response["Preview of `{schema}.{table}` — does this look correct?"]
    next_action = response["What would you like to do next?"]

    # Store all answers
    state.update({
        "schema": schema,
        "table": table,
        "preview_action": preview_action,
        "next_action": next_action
    })

    return state, (schema, table, preview_action, next_action)
```

---

## State Management

### Load at Start of Each Turn
```python
import json
from pathlib import Path

STATE_FILE = Path(".auto-cdq-state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "workflow": None,
        "phase": None,
        "schema": None,
        "table": None,
        "dataset": None,
        "limit": None,
        "selected_rules": [],
        "backward_navigation": {},
    }

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def clear_state():
    if STATE_FILE.exists():
        STATE_FILE.unlink()
```

---

## Backend Skills to Call

Use these existing CDQ skills inside your batch handlers:

| Skill | When | Example |
|-------|------|---------|
| `cdq-list-tables` | Browse/search tables | `cdq-list-tables --schema samples --search "%cust%" --limit 20` |
| `cdq-run-sql` | Preview data | `cdq-run-sql --sql "SELECT * FROM samples.customers LIMIT 5"` |
| `cdq-run-dq-job` | Onboard dataset | `cdq-run-dq-job --dataset customers_dq --sql "SELECT * FROM samples.customers LIMIT 10000"` |
| `cdq-workflow-suggest-rules` | Analyze columns | `cdq-workflow-suggest-rules --dataset customers_dq` |
| `cdq-save-rule` | Create rule | `cdq-save-rule --dataset customers_dq --name "Completeness: email" --sql "SELECT * FROM ..."` |
| `cdq-test-connection` | Verify API | `cdq-test-connection` |

---

## Backward Navigation Handling

When user presses ← to go back, detect and re-show batch with pre-filled answers:

```python
def handle_backward_navigation(state, from_section, to_section):
    """
    User wants to revisit earlier section.
    Re-show batch with pre-filled answers.
    """
    # Get previous answers to pre-fill
    schema = state.get("schema")
    table = state.get("table")

    # Track navigation
    state["backward_navigation"] = {
        "from_section": from_section,
        "to_section": to_section,
        "revisit_count": state.get("backward_navigation", {}).get("revisit_count", 0) + 1
    }

    # Re-show batch with answers pre-selected
    # (CLI will show checkmarks and allow modification)
    response = AskUserQuestion(questions=[...])  # Same batch as before

    return response  # User can now modify earlier selections
```

---

## Response Dictionary Structure

After user answers all 4 questions in a batch:

```python
response = AskUserQuestion(questions=[...])  # After Phase 2 Discovery

print(response)
# {
#   "Which schema should we search in?": "samples",
#   "Which table would you like to work with?": "customers",
#   "Preview of `samples.customers` — does this look correct?": "Yes, use this table (Recommended)",
#   "What would you like to do next?": "Start onboarding (Recommended)"
# }

# NOT:
# {
#   "Schema": "samples",  # ❌ Wrong key
#   "Table": "customers",  # ❌ Wrong key
# }
```

**Rule:** Dictionary keys = full question text (NOT header)

---

## CLI Rendering Preview

What user sees as they navigate:

```
STEP 1: Initial state
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which schema should we search in?
❯ 1. samples (Recommended)
  2. Type something else
  3. Chat about this

[User selects option 1 and presses Enter]

STEP 2: After first answer
✓ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which table would you like to work with?
❯ 1. customers (Recommended)
  2. Search by pattern
  3. Browse all tables

[User presses →]

STEP 3: Navigate to next section
✓ Schema    ✓ Table    ☐ Preview    ☐ Next Step

Preview of `samples.customers` — does this look correct?
❯ 1. Yes, use this table (Recommended)
  2. Preview more rows
  3. Choose different table

[User presses ←]

STEP 4: Go back to Schema
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which schema should we search in? [can modify]
❯ 1. samples (Recommended) [previously selected]
  2. Type something else
```

---

## Workflow Decision Tree

```
User invokes /auto-cdq
│
├─ Show Workflow menu (1 section)
│  ├──> Discovery
│  ├──> Onboarding
│  ├──> Rules
│  └──> Exit
│
├─ Discovery selected
│  └──> Phase 2: 4-section batch (Schema | Table | Preview | Next)
│       └──> Next="Onboarding" → Onboarding workflow
│       └──> Next="Rules" → Rules workflow
│       └──> Next="Preview another" → Loop back to Phase 2
│       └──> "Exit" → Clear state, end session
│
├─ Onboarding selected
│  ├──> Phase 1: Discovery 4-section batch (reused)
│  └──> Phase 2: 4-section batch (Dataset | Size | Validation | Confirm)
│       └──> Execution: Run job
│
└─ Rules selected
   ├──> Phase 1: Discovery 4-section batch (reused)
   └──> Phase 2: 4-section batch (Analysis | Selection | Testing | Save)
        └──> Execution: Save rules
```

---

## Testing This Works

After implementing the batch pattern:

```bash
# Test Discovery workflow shows all 4 sections
/auto-cdq discovery

# You should see:
# ☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

# Test arrow key navigation (← / →)
# Test backward navigation (press ← from Preview, modify Schema, press → forward)
# Test Exit at each section clears state

# Verify state file created
cat .auto-cdq-state.json
# Should show all answers from 4-section batch
```

---

## Common Mistakes to Avoid

❌ **Don't** ask all questions separately:
```python
response1 = AskUserQuestion(questions=[{"header": "Schema", ...}])
response2 = AskUserQuestion(questions=[{"header": "Table", ...}])  # ❌ Breaks multi-section
```

✅ **Do** batch into one call:
```python
response = AskUserQuestion(questions=[
    {"header": "Schema", ...},
    {"header": "Table", ...},
    {"header": "Preview", ...},
    {"header": "Next Step", ...}
])
```

---

❌ **Don't** use header as dict key:
```python
schema = response["Schema"]  # ❌ KeyError
```

✅ **Do** use full question text:
```python
schema = response["Which schema should we search in?"]  # ✅ Correct
```

---

❌ **Don't** make more than 4 sections per batch:
```python
# ❌ 5 questions = won't render properly
response = AskUserQuestion(questions=[q1, q2, q3, q4, q5])
```

✅ **Do** split into multiple phases:
```python
# ✅ Phase 1
response1 = AskUserQuestion(questions=[q1, q2, q3, q4])
# ✅ Phase 2
response2 = AskUserQuestion(questions=[q5, q6, q7, q8])
```

---

## Reference Files

Use these when building:

1. **SKILL.md** (lines 79-187) — Discovery implementation spec
2. **SKILL.md** (lines 209-272) — Onboarding implementation spec
3. **SKILL.md** (lines 274-349) — Rules implementation spec
4. **IMPLEMENTATION_CHECKLIST.md** — Validation criteria (50+ tests)
5. **GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md** — Detailed walkthrough

---

## You're Ready! 🚀

This is everything you need to:
1. Understand the pattern
2. Code the implementation
3. Test the result
4. Validate against checklist

**Questions?** See GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md for deep dive.
