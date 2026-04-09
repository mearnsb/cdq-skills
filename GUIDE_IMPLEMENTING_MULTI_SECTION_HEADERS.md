# Implementation Guide: Multi-Section Headers for auto-cdq

This guide shows step-by-step how to refactor auto-cdq to display multi-section headers like autoresearch.

---

## Before: Single Section (Current)

When you invoke `/auto-cdq discovery`, you see:

```
─────────────────────────────────────────
 ☐ Schema

Which schema should we search in?

❯ 1. samples (Recommended)
  2. Type something else
  3. Chat about this
─────────────────────────────────────────
```

**Problem:** Only one section visible. User must answer sequentially without seeing the overall journey.

---

## After: Multi-Section Headers (Improved)

Same workflow, but now you see:

```
─────────────────────────────────────────
 ☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which schema should we search in?

❯ 1. samples (Recommended)
  2. Type something else
  3. Chat about this
─────────────────────────────────────────
```

**Benefits:**
- User sees the full 4-step journey upfront
- Can navigate left/right with arrow keys to revisit schema, change table choice, etc.
- Checkmarks (✓) appear as each section completes
- Natural flow from discovery → preview → next action

---

## Step 1: Understand the Current auto-cdq Structure

From the existing SKILL.md:

```markdown
## Discovery Workflow

### Phase 1: Schema Selection
**1.1** Get schema from .env
**1.2** Present schema menu
**1.3** Handle answer

### Phase 2: Table Selection
**2.1** Present table menu
...

### Phase 3: Preview
**3.1** Run preview
...

### Phase 4: Post-Discovery Menu
```

**Current implementation:** Each phase calls `AskUserQuestion` separately:

```python
# Phase 1
response1 = AskUserQuestion(
  questions=[
    {
      "question": "Which schema should we search in?",
      "header": "Schema",
      "multiSelect": false,
      "options": [...]
    }
  ]
)

# Later... Phase 2
response2 = AskUserQuestion(
  questions=[
    {
      "question": "Which table would you like to work with?",
      "header": "Table",
      "multiSelect": false,
      "options": [...]
    }
  ]
)

# Later... Phase 3
response3 = AskUserQuestion(
  questions=[...]
)
```

**Problem:** Each call is independent. No visual connection between them.

---

## Step 2: Refactor to Batch Questions (Max 4 Per Call)

**Goal:** Show Schema → Table → Preview → Next Step as a single 4-section header bar.

**Solution:** Combine all 4 questions into ONE `AskUserQuestion` call:

```python
AskUserQuestion(
  questions=[
    {
      "question": "Which schema should we search in?",
      "header": "Schema",
      "multiSelect": false,
      "options": [
        {"label": "samples (Recommended)", "description": "..."},
        {"label": "Type something else", "description": "..."},
        {"label": "Chat about this", "description": "..."}
      ]
    },
    {
      "question": "Which table would you like to work with?",
      "header": "Table",
      "multiSelect": false,
      "options": [
        {"label": "customers (Recommended)", "description": "..."},
        {"label": "Search by pattern", "description": "..."},
        {"label": "Browse all tables", "description": "..."}
      ]
    },
    {
      "question": "Preview of table — what would you like to do?",
      "header": "Preview",
      "multiSelect": false,
      "options": [
        {"label": "Use this table (Recommended)", "description": "..."},
        {"label": "Preview more rows", "description": "..."},
        {"label": "Choose different table", "description": "..."}
      ]
    },
    {
      "question": "What would you like to do next?",
      "header": "Next Step",
      "multiSelect": false,
      "options": [
        {"label": "Start onboarding (Recommended)", "description": "..."},
        {"label": "Create rules", "description": "..."},
        {"label": "Exit", "description": "..."}
      ]
    }
  ]
)
```

**Result:**
```
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step
```

---

## Step 3: Handle User Responses

When the user answers all 4 questions in the batched call, the response contains all 4 answers:

```python
response = AskUserQuestion(questions=[...])

# response is a dict like:
# {
#   "Which schema should we search in?": "samples",
#   "Which table would you like to work with?": "customers",
#   "Preview of table — what would you like to do?": "Use this table (Recommended)",
#   "What would you like to do next?": "Start onboarding (Recommended)"
# }

schema = response.get("Which schema should we search in?")
table = response.get("Which table would you like to work with?")
preview_action = response.get("Preview of table — what would you like to do?")
next_step = response.get("What would you like to do next?")
```

---

## Step 4: Support Backward Navigation

The key to making multi-section headers work is **supporting the user's ability to revisit earlier sections**.

When the user presses ← to go back, Claude Code **re-displays the previous batched questions**, but now some sections show ✓ (completed).

**Implementation strategy:**

1. **Store state** in `.auto-cdq-state.json`:
   ```json
   {
     "phase": "discovery",
     "schema": "samples",
     "table": null,
     "preview_confirmed": false,
     "next_action": null
   }
   ```

2. **When user navigates backward**, detect which section they're revisiting and re-ask:
   ```python
   # User pressed ← while viewing "Next Step", wants to revisit "Preview"
   # Re-show the batched questions, but with earlier answers already filled in

   AskUserQuestion(
     questions=[
       # Schema section — already answered "samples"
       {
         "question": "Which schema should we search in?",
         "header": "Schema ✓",  # Show checkmark
         "multiSelect": false,
         "options": [...]  # Pre-select "samples"
       },
       # Table section — already answered "customers"
       {
         "question": "Which table would you like to work with?",
         "header": "Table ✓",  # Show checkmark
         "multiSelect": false,
         "options": [...]  # Pre-select "customers"
       },
       # Preview section — user is here NOW
       {
         "question": "Preview of table — what would you like to do?",
         "header": "Preview",  # No checkmark, this is current
         "multiSelect": false,
         "options": [...]
       },
       # Next Step — grayed out or not shown yet
     ]
   )
   ```

---

## Step 5: Progressive Disclosure Pattern

Don't ask all questions at once. Use phases:

### Phase 1: Workflow Selection (1 Question)
Show user what they want to do (Discovery, Onboarding, Rules).

```
☐ Workflow

"What would you like to do?"
- Discovery (Recommended)
- Onboarding
- Rules
```

### Phase 2: Table Discovery (3 Questions)
User selects schema → table → preview.

```
☐ Schema    ☐ Table    ☐ Preview

Question 1: "Which schema?"
Question 2: "Which table?"
Question 3: "Preview looks good?"
```

### Phase 3: Confirm & Next (2 Questions)
Final confirmation and what to do next.

```
☐ Confirm    ☐ Next Step

Question 1: "Ready to proceed?"
Question 2: "What next? Onboard / Create Rules / Exit"
```

**Benefits:**
- Not overwhelming (max 3-4 sections per batch)
- User sees clear progress through discovery → preview → action
- Natural stopping points between phases
- Each phase can be revisited independently

---

## Concrete Example: Discovery Workflow With Headers

```python
#!/usr/bin/env python3
"""
auto-cdq Discovery Workflow with Multi-Section Headers
"""

import json
from pathlib import Path

STATE_FILE = Path(".auto-cdq-state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "phase": "discovery",
        "workflow": None,
        "schema": None,
        "table": None,
        "preview_data": None,
        "next_action": None
    }

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def discovery_workflow():
    state = load_state()

    # PHASE 1: Workflow selection (single section)
    print("=" * 60)
    print("PHASE 1: Select Workflow")
    print("=" * 60)

    workflow_response = AskUserQuestion(
        questions=[
            {
                "question": "What would you like to do?",
                "header": "Workflow",
                "multiSelect": False,
                "options": [
                    {"label": "Discovery (Recommended)", "description": "Find and preview tables"},
                    {"label": "Onboarding", "description": "Register a dataset"},
                    {"label": "Rules", "description": "Create data quality rules"},
                    {"label": "Exit", "description": "End session"}
                ]
            }
        ]
    )

    state["workflow"] = workflow_response["What would you like to do?"]
    if state["workflow"] == "Exit":
        save_state({})  # Clear state
        print("Goodbye!")
        return

    save_state(state)

    # PHASE 2: Table Discovery (3 sections visible)
    print("\n" + "=" * 60)
    print("PHASE 2: Discover Table")
    print("=" * 60)
    print("You'll see: Schema | Table | Preview")

    discovery_response = AskUserQuestion(
        questions=[
            {
                "question": "Which schema should we search in?",
                "header": "Schema",
                "multiSelect": False,
                "options": [
                    {"label": "samples (Recommended)", "description": "Configured schema"},
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
                    {"label": "Search by pattern", "description": "Find with pattern"},
                    {"label": "Browse all tables", "description": "List all"},
                    {"label": "Type something else", "description": "Custom table"}
                ]
            },
            {
                "question": "Does the preview look correct?",
                "header": "Preview",
                "multiSelect": False,
                "options": [
                    {"label": "Yes, use this table (Recommended)", "description": "Proceed"},
                    {"label": "Preview more rows", "description": "Show 20 rows"},
                    {"label": "Choose different table", "description": "Back to table selection"},
                    {"label": "Chat about this", "description": "Discuss"}
                ]
            }
        ]
    )

    state["schema"] = discovery_response["Which schema should we search in?"]
    state["table"] = discovery_response["Which table would you like to work with?"]
    state["preview_action"] = discovery_response["Does the preview look correct?"]

    save_state(state)

    # PHASE 3: Confirm & Next Steps (2 sections visible)
    print("\n" + "=" * 60)
    print("PHASE 3: Confirm & Plan Next Steps")
    print("=" * 60)
    print(f"Schema: {state['schema']}")
    print(f"Table: {state['table']}")

    confirm_response = AskUserQuestion(
        questions=[
            {
                "question": f"Ready to proceed with {state['schema']}.{state['table']}?",
                "header": "Confirm",
                "multiSelect": False,
                "options": [
                    {"label": "Yes, proceed (Recommended)", "description": "Continue"},
                    {"label": "Change table", "description": "Go back to Phase 2"},
                    {"label": "Exit", "description": "End session"}
                ]
            },
            {
                "question": "What would you like to do next?",
                "header": "Next Step",
                "multiSelect": False,
                "options": [
                    {"label": "Start onboarding (Recommended)", "description": "Register dataset"},
                    {"label": "Create rules", "description": "Begin rule creation"},
                    {"label": "Exit", "description": "End session"}
                ]
            }
        ]
    )

    state["confirmed"] = confirm_response["Ready to proceed with...?"]
    state["next_action"] = confirm_response["What would you like to do next?"]

    save_state(state)

    print("\n" + "=" * 60)
    print("DISCOVERY COMPLETE")
    print("=" * 60)
    print(f"Schema: {state['schema']}")
    print(f"Table: {state['table']}")
    print(f"Next Action: {state['next_action']}")
    print("\nState saved to .auto-cdq-state.json")

if __name__ == "__main__":
    discovery_workflow()
```

---

## Expected CLI Output

**PHASE 1:**
```
☐ Workflow

"What would you like to do?"
❯ 1. Discovery (Recommended)
  2. Onboarding
  3. Rules
  4. Exit
```

**PHASE 2 (After Phase 1 complete, user presses Enter):**
```
✓ Workflow    ☐ Schema    ☐ Table    ☐ Preview

"Which schema should we search in?"
❯ 1. samples (Recommended)
  2. Type something else
  3. Chat about this
```

*User presses → to navigate to next section:*

```
✓ Workflow    ✓ Schema    ☐ Table    ☐ Preview

"Which table would you like to work with?"
❯ 1. customers (Recommended)
  2. Search by pattern
  3. Browse all tables
  4. Type something else
```

*User presses ← to go back:*

```
✓ Workflow    ☐ Schema    ☐ Table    ☐ Preview

"Which schema should we search in?" [Can change answer]
❯ 1. samples (Recommended)
  2. Type something else
  3. Chat about this
```

---

## Key Implementation Points

| Feature | How to Implement |
|---------|-----------------|
| **Max 4 sections per batch** | Group questions into single `AskUserQuestion` calls (max 4 questions) |
| **Unique header for each question** | Set `header: "Section Name"` on each question |
| **Checkmark tracking (✓)** | Automatic — Claude Code's CLI handles this |
| **Navigation (← / →)** | Automatic — Claude Code's CLI handles this |
| **Support backward navigation** | Store state, re-display batches when user goes back |
| **Visual state persistence** | Each section shows ✓ if already answered, ☐ if pending |
| **Allow answer modification** | When user presses ← to earlier section, let them change selection |

---

## Migration Checklist

When updating auto-cdq to use multi-section headers:

- [ ] Group Discovery Phase 1-3 into one 4-question batch
- [ ] Group Onboarding Phase 1-3 into one 3-4-question batch
- [ ] Group Rules Phase 1-3 into one 4-question batch
- [ ] Update state tracking to handle all answers from batch
- [ ] Add support for detecting backward navigation (user wants to revisit earlier section)
- [ ] Test with actual Claude Code CLI to verify header rendering
- [ ] Test arrow key navigation (← / →) between sections
- [ ] Test answer modification when revisiting earlier sections
- [ ] Document the section flow in SKILL.md (show the visual header bar expected at each phase)

---

## Why This Works Better

1. **Visual Journey**: User sees full workflow at a glance (e.g., Schema → Table → Preview → Action)
2. **Backward Navigation**: Easy to revisit and change earlier decisions
3. **Reduced Cognitive Load**: Not asking questions in sequence; showing progression
4. **Professional UX**: Mimics workflows in modern tools (setup wizards, multi-step forms)
5. **Faster Interaction**: User can navigate with arrow keys instead of typing answers

---

## Additional Resources

- **autoresearch SKILL.md** — Reference implementation (lines 265-299)
- **Claude Code docs** — Skills section on AskUserQuestion
- **auto-cdq SKILL.md** — Current implementation to enhance
