# Analysis: Multi-Section Header Navigation in Claude Code

## Executive Summary

**YES, multi-section header navigation is absolutely possible for auto-cdq.** This analysis examines how autoresearch implements visual state tracking and shows how to apply the same pattern to auto-cdq.

The key insight: **Section headers are rendered by Claude Code's CLI UI based on the `header` field in `AskUserQuestion`** — not by your code. Claude Code automatically maintains visual state across multiple questions.

---

## How autoresearch Implements Multi-Section Headers

### What You See (Visual Output)

When using autoresearch, you see:

```
☐ Goal          ☐ Scope          ☐ Metric          ☐ Direction
```

Each section is:
- **Unchecked (☐)** when pending
- **Checked (✓)** when completed with an answer
- **Navigable** with arrow keys to move left/right between sections
- **Editable** — you can revisit earlier sections and change answers

### How It Works (Technical Implementation)

Looking at the autoresearch SKILL.md, the pattern is:

**Batch 1 — Four questions in a single `AskUserQuestion` call:**

```yaml
AskUserQuestion:
  question: "What do you want to improve?"
  header: "Goal"
  multiSelect: false
  options: [...]

AskUserQuestion:
  question: "Which files can autoresearch modify?"
  header: "Scope"
  multiSelect: false
  options: [...]

AskUserQuestion:
  question: "What number tells you if it got better?"
  header: "Metric"
  multiSelect: false
  options: [...]

AskUserQuestion:
  question: "Higher or lower is better?"
  header: "Direction"
  multiSelect: false
  options: [...]
```

**Key insight:** Each question gets its own `header` field. Claude Code's CLI renders these as a horizontal list of sections at the top.

From `autoresearch/.claude/skills/autoresearch/SKILL.md` (lines 265-285):

> **Batch 1 — Core config (4 questions in one call):**
>
> Use a SINGLE `AskUserQuestion` call with these 4 questions:
>
> | # | Header | Question | Options |
> |---|--------|----------|---------|
> | 1 | `Goal` | "What do you want to improve?" | ... |
> | 2 | `Scope` | "Which files can autoresearch modify?" | ... |
> | 3 | `Metric` | "What number tells you if it got better?" | ... |
> | 4 | `Direction` | "Higher or lower is better?" | ... |

---

## Critical Rules for Multi-Section Headers

### 1. **Use Batched Questions (Max 4 Per Batch)**

The CLI can display up to **4 section headers simultaneously**. Group related questions into single `AskUserQuestion` calls:

```python
AskUserQuestion(
  questions=[
    {
      "question": "Question 1",
      "header": "Section 1",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Question 2",
      "header": "Section 2",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Question 3",
      "header": "Section 3",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Question 4",
      "header": "Section 4",
      "multiSelect": false,
      "options": [...]
    }
  ]
)
```

### 2. **Each Question Gets a Unique Header**

The `header` field becomes a section label:

```python
{
  "question": "Which table would you like to work with?",
  "header": "Table",           # ← This becomes the section header
  "multiSelect": false,
  "options": [...]
}
```

### 3. **Navigation Is Automatic**

Claude Code's CLI provides:
- **Arrow keys** (← / →) to navigate between sections
- **Checkbox tracking** (☐ → ✓) showing completion status
- **Ability to revisit** earlier sections and change answers

---

## How to Apply This to auto-cdq

### Current Implementation (Single Section)

```python
AskUserQuestion(
  questions=[
    {
      "question": "Which schema should we search in?",
      "header": "Schema",
      "multiSelect": false,
      "options": [...]
    }
  ]
)
```

Result: Only one section visible at a time (☐ Schema).

### Improved Implementation (Multi-Section)

**Discovery Workflow Phase 1: Schema + Initial Setup**

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
      "question": "What would you like to do?",
      "header": "Action",
      "multiSelect": false,
      "options": [
        {"label": "Explore tables (Recommended)", "description": "..."},
        {"label": "Onboard a dataset", "description": "..."},
        {"label": "Create rules", "description": "..."}
      ]
    }
  ]
)
```

Result: Two sections visible (☐ Schema → ☐ Action), user can navigate left/right.

**Discovery Workflow Phase 2: Schema + Table Selection**

```python
AskUserQuestion(
  questions=[
    {
      "question": "Which schema should we search in?",
      "header": "Schema",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Which table would you like to work with?",
      "header": "Table",
      "multiSelect": false,
      "options": [...]
    }
  ]
)
```

Result:
- Section 1 (Schema) shows ✓ (completed in previous batch)
- Section 2 (Table) shows ☐ (pending, current question)
- User can press ← to go back and re-select schema if needed

**Discovery Workflow Phase 3: Full Journey (4 Sections)**

```python
AskUserQuestion(
  questions=[
    {
      "question": "Which schema should we search in?",
      "header": "Schema",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Which table would you like to work with?",
      "header": "Table",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Preview matches your needs?",
      "header": "Preview",
      "multiSelect": false,
      "options": [
        {"label": "Yes, use this table (Recommended)", "description": "..."},
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

Result: Full header bar:
```
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step
```

When the user answers all 4, they can press ← to revisit any section.

---

## Design Pattern: Progressive Disclosure

The autoresearch workflow uses **progressive disclosure** — showing sections as the user advances:

1. **Batch 1** (Setup Phase): Show all config questions upfront
   ```
   ☐ Goal    ☐ Scope    ☐ Metric    ☐ Direction
   ```

2. **Batch 2** (Verification Phase): Show verify + guard + launch
   ```
   ☐ Verify    ☐ Guard    ☐ Launch
   ```

3. **Loop Phase** (Execution): No more questions — just output

This prevents **cognitive overload** (not asking 20 questions at once) while still letting users **navigate backwards** to reconsider earlier choices.

---

## Recommended Structure for auto-cdq

### Phase 1: Workflow Selection (1 Question)
```
☐ Workflow
```

### Phase 2: Table Discovery (3 Questions)
```
☐ Schema    ☐ Table    ☐ Preview
```

### Phase 3: Onboarding Config (4 Questions)
```
☐ Dataset Name    ☐ Sample Size    ☐ Validation    ☐ Confirm
```

### Phase 4: Rules Analysis (4 Questions)
```
☐ Column Analysis    ☐ Rule Selection    ☐ Rule Testing    ☐ Save Rules
```

---

## Implementation Checklist

- [ ] **Group questions by phase**: Max 4 questions per `AskUserQuestion` call
- [ ] **Use meaningful headers**: Each header becomes a visible section
- [ ] **Store state progressively**: Update `.auto-cdq-state.json` after each batch
- [ ] **Allow navigation**: Don't clear earlier sections when moving forward
- [ ] **Mark sections as complete**: The ✓ checkbox appears automatically once answered
- [ ] **Support backward navigation**: When user presses ← in CLI, be ready to show earlier sections again

---

## Example: Full Discovery Workflow with Multi-Section Headers

```python
# Phase 1: Select workflow
response1 = AskUserQuestion(
  questions=[
    {
      "question": "What would you like to do?",
      "header": "Workflow",
      "multiSelect": false,
      "options": [
        {"label": "Discovery (Recommended)", "description": "Find tables"},
        {"label": "Onboarding", "description": "Register dataset"},
        {"label": "Rules", "description": "Create rules"},
      ]
    }
  ]
)

# Phase 2: Table discovery (3 sections visible)
response2 = AskUserQuestion(
  questions=[
    {
      "question": "Which schema?",
      "header": "Schema",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Which table?",
      "header": "Table",
      "multiSelect": false,
      "options": [...]
    },
    {
      "question": "Preview good?",
      "header": "Preview",
      "multiSelect": false,
      "options": [...]
    }
  ]
)

# Phase 3: Next steps (2 sections visible)
response3 = AskUserQuestion(
  questions=[
    {
      "question": "What next?",
      "header": "Next Step",
      "multiSelect": false,
      "options": [
        {"label": "Create rules (Recommended)", "description": "..."},
        {"label": "Exit", "description": "..."}
      ]
    }
  ]
)
```

---

## Key Takeaway

**The multi-section header bar is built into Claude Code's CLI.** You don't need special code to render it — just:

1. **Group your questions** into batches (max 4 per `AskUserQuestion` call)
2. **Give each question a unique `header`** field
3. **Store state** so you know where the user is in the workflow
4. **Support revisiting earlier sections** by re-showing them if the user navigates backward

Claude Code handles the visual rendering, navigation keys, and checkbox tracking automatically.

---

## References

- **autoresearch SKILL.md**, lines 265-299 (Setup Phase implementation)
- **Claude Code docs**: Skills section on `AskUserQuestion` batching
- **auto-cdq SKILL.md**: Current single-section implementation to enhance
