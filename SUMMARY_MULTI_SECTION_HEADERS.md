# Summary: Multi-Section Headers for auto-cdq

## Your Question
> Can auto-cdq show all sections left-to-right along the top (like autoresearch) with ✓/☐ checkmarks and arrow key navigation?

## Answer
**YES, absolutely.** This is built into Claude Code's CLI and already used by autoresearch. You just need to structure your questions differently.

---

## How It Currently Works (Single Section)

```
─────────────────────────────
 ☐ Schema

Which schema should we search in?
❯ 1. samples
  2. Type something else
─────────────────────────────
```

**Problem:** Only one section visible. No visual indication of the workflow steps.

---

## How It Can Work (Multi-Section Headers)

```
─────────────────────────────
 ☐ Schema    ☐ Table    ☐ Preview    ☐ Confirm

Which schema should we search in?
❯ 1. samples (Recommended)
  2. Type something else
─────────────────────────────
```

**Benefits:**
- User sees full 4-step journey upfront
- Can navigate with arrow keys (← →) to revisit sections
- Checkmarks (✓) appear as each section completes
- Natural, professional UX like modern setup wizards

---

## The Secret: Batch Your Questions

**Current approach (4 separate calls):**
```python
# Call 1
AskUserQuestion(questions=[{"header": "Schema", ...}])

# Call 2 (later)
AskUserQuestion(questions=[{"header": "Table", ...}])

# Call 3 (later)
AskUserQuestion(questions=[{"header": "Preview", ...}])

# Call 4 (later)
AskUserQuestion(questions=[{"header": "Confirm", ...}])
```

**Better approach (1 batched call):**
```python
AskUserQuestion(questions=[
    {"header": "Schema", ...},
    {"header": "Table", ...},
    {"header": "Preview", ...},
    {"header": "Confirm", ...}
])
```

**Result:** All 4 sections appear in header bar automatically.

---

## Key Rules

1. **Max 4 sections per batch** — Claude Code CLI hard limit
2. **Each question gets unique `header`** — That becomes a visible section
3. **Store state** — Track answers in `.auto-cdq-state.json`
4. **Support backward nav** — User can press ← to revisit earlier sections
5. **No code tricks needed** — Claude Code handles all the UI rendering

---

## Recommended Structure for auto-cdq

### Phase 1: Workflow Selection
```
☐ Workflow
(1 section)
```

### Phase 2: Discovery
```
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step
(4 sections)
```

### Phase 3: Onboarding
```
☐ Dataset Name    ☐ Sample Size    ☐ Validation    ☐ Confirm
(4 sections)
```

### Phase 4: Rules
```
☐ Analysis    ☐ Rules    ☐ Testing    ☐ Save
(4 sections)
```

---

## Example: Phase 2 Discovery (Current Code)

**Before (single sections):**
```python
# First question
schema_response = AskUserQuestion(questions=[{
    "question": "Which schema?",
    "header": "Schema",
    "options": [...]
}])

# Second question (separate call)
table_response = AskUserQuestion(questions=[{
    "question": "Which table?",
    "header": "Table",
    "options": [...]
}])

# And so on...
```

**After (batched):**
```python
# All 4 questions in one call
discovery_response = AskUserQuestion(questions=[
    {
        "question": "Which schema should we search in?",
        "header": "Schema",
        "multiSelect": false,
        "options": [
            {"label": "samples (Recommended)", "description": "..."},
            {"label": "Type something else", "description": "..."}
        ]
    },
    {
        "question": "Which table would you like to work with?",
        "header": "Table",
        "multiSelect": false,
        "options": [
            {"label": "customers (Recommended)", "description": "..."},
            {"label": "Search by pattern", "description": "..."}
        ]
    },
    {
        "question": "Does the preview look correct?",
        "header": "Preview",
        "multiSelect": false,
        "options": [
            {"label": "Yes, use this (Recommended)", "description": "..."},
            {"label": "Preview more rows", "description": "..."}
        ]
    },
    {
        "question": "What would you like to do next?",
        "header": "Next Step",
        "multiSelect": false,
        "options": [
            {"label": "Start onboarding", "description": "..."},
            {"label": "Create rules", "description": "..."}
        ]
    }
])

# Now you have all 4 answers
schema = discovery_response["Which schema should we search in?"]
table = discovery_response["Which table would you like to work with?"]
preview_action = discovery_response["Does the preview look correct?"]
next_step = discovery_response["What would you like to do next?"]
```

---

## What You See in CLI

### Question 1 (Schema)
```
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which schema should we search in?
❯ 1. samples (Recommended)
  2. Type something else
```

### After pressing Enter (moves to Question 2)
```
✓ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which table would you like to work with?
❯ 1. customers (Recommended)
  2. Search by pattern
```

### After pressing ← (goes back to Schema)
```
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which schema should we search in?
❯ 1. samples (Recommended)  [Can change answer]
  2. Type something else
```

---

## Implementation Checklist

- [ ] Update auto-cdq SKILL.md to batch questions (max 4 per call)
- [ ] Refactor Discovery Phase to use 1 batched call (4 questions)
- [ ] Refactor Onboarding Phase to use 1 batched call (3-4 questions)
- [ ] Refactor Rules Phase to use 1 batched call (4 questions)
- [ ] Update state management to handle batched responses
- [ ] Test with actual Claude Code CLI
- [ ] Verify arrow key navigation (← →) works
- [ ] Verify answer modification when navigating backward
- [ ] Update SKILL.md documentation with visual examples

---

## Reference Documents

Created for you:

1. **ANALYSIS_MULTI_SECTION_HEADERS.md**
   - Deep dive into how autoresearch implements this pattern
   - Technical breakdown of Claude Code's CLI rendering
   - Critical rules and patterns

2. **GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md**
   - Step-by-step refactoring guide
   - Before/after code examples
   - Concrete Python example of full discovery workflow
   - Progressive disclosure pattern explanation

3. **This summary** — Quick reference

---

## Source Pattern

The autoresearch skill implements exactly this pattern at lines 265-299 of `.claude/skills/autoresearch/SKILL.md`:

```markdown
### Interactive Setup (when invoked without full config)

Batch 1 — Core config (4 questions in one call):

Use a SINGLE `AskUserQuestion` call with these 4 questions:

| # | Header | Question | Options |
|---|--------|----------|---------|
| 1 | `Goal` | "What do you want to improve?" | ... |
| 2 | `Scope` | "Which files can autoresearch modify?" | ... |
| 3 | `Metric` | "What number tells you if it got better?" | ... |
| 4 | `Direction` | "Higher or lower is better?" | ... |
```

This produces the header bar:
```
☐ Goal    ☐ Scope    ☐ Metric    ☐ Direction
```

Same technique works perfectly for auto-cdq.

---

## Next Steps

1. **Read the detailed guides** — See ANALYSIS and GUIDE documents for full context
2. **Update auto-cdq SKILL.md** — Batch the questions according to workflow phases
3. **Test in CLI** — Run `/auto-cdq discovery` and verify header bar appears
4. **Iterate** — Adjust question grouping if needed

This is a pure UX improvement — no backend changes required. Just regroup your questions and let Claude Code's CLI do the rendering.

---

## Questions?

The pattern is:
- **One `AskUserQuestion` call** = multiple section headers visible
- **Multiple calls** = sections appear one at a time

Group related questions into single batches for the multi-section header effect.
