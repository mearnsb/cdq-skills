# Quick Reference: Multi-Section Headers

## The One Trick

**Group your questions differently:**

```python
# ❌ OLD (one section at a time)
response1 = AskUserQuestion(questions=[{"header": "Schema", ...}])
response2 = AskUserQuestion(questions=[{"header": "Table", ...}])

# ✅ NEW (all sections at once)
response = AskUserQuestion(questions=[
    {"header": "Schema", ...},
    {"header": "Table", ...},
    {"header": "Preview", ...},
    {"header": "Confirm", ...}
])
```

---

## What the User Sees

```
☐ Schema    ☐ Table    ☐ Preview    ☐ Confirm

Which schema should we search in?
❯ 1. samples (Recommended)
  2. Type something else
```

User presses → (or Enter) to move to next section:

```
✓ Schema    ☐ Table    ☐ Preview    ☐ Confirm

Which table would you like to work with?
❯ 1. customers (Recommended)
  2. Search by pattern
```

User presses ← to go back:

```
☐ Schema    ☐ Table    ☐ Preview    ☐ Confirm

Which schema should we search in? [can modify]
```

---

## Key Rules

| Rule | Details |
|------|---------|
| **Max 4 per batch** | Claude Code CLI hard limit |
| **One question per section** | Each `header` = one visible section |
| **Unique headers** | Different names for each section |
| **State management** | Store answers in `.auto-cdq-state.json` |
| **Backward nav** | Support user pressing ← to revisit earlier sections |

---

## Implementation Checklist

- [ ] Identify your 4-step workflow (or break into phases of 4)
- [ ] Create 4 questions (one per section)
- [ ] Give each question a unique `header` field
- [ ] Put all 4 in ONE `AskUserQuestion` call
- [ ] Extract answers from response dict:
  ```python
  response = AskUserQuestion(questions=[...])
  schema = response["Which schema...?"]
  table = response["Which table...?"]
  # etc.
  ```
- [ ] Update state tracking
- [ ] Test in CLI: `/auto-cdq discovery`
- [ ] Verify header bar shows all 4 sections
- [ ] Test arrow key navigation
- [ ] Update SKILL.md documentation

---

## Before vs After Code

### Before (Single Section)
```python
# Question 1
schema_response = AskUserQuestion(questions=[{
    "question": "Which schema should we search in?",
    "header": "Schema",
    "multiSelect": false,
    "options": [
        {"label": "samples (Recommended)", "description": "..."},
        {"label": "Type something else", "description": "..."}
    ]
}])
schema = schema_response["Which schema should we search in?"]

# Question 2 (separate)
table_response = AskUserQuestion(questions=[{
    "question": "Which table would you like to work with?",
    "header": "Table",
    "multiSelect": false,
    "options": [...]
}])
table = table_response["Which table would you like to work with?"]
```

### After (Multi-Section)
```python
response = AskUserQuestion(questions=[
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
        "options": [...]
    },
    {
        "question": "Does the preview look correct?",
        "header": "Preview",
        "multiSelect": false,
        "options": [...]
    },
    {
        "question": "What would you like to do next?",
        "header": "Confirm",
        "multiSelect": false,
        "options": [...]
    }
])

# Extract all answers
schema = response["Which schema should we search in?"]
table = response["Which table would you like to work with?"]
preview_ok = response["Does the preview look correct?"]
next_action = response["What would you like to do next?"]
```

---

## Recommended Workflow Structure

```
Phase 1: Workflow Selection (1 section)
  ├─ Batch 1: "What would you like to do?"

Phase 2: Discovery (4 sections)
  ├─ Batch 1: Schema | Table | Preview | Next Step

Phase 3: Onboarding (4 sections)
  ├─ Batch 1: Dataset Name | Sample Size | Validation | Confirm

Phase 4: Rules (4 sections)
  ├─ Batch 1: Analysis | Rules | Testing | Save
```

---

## CLI Usage

```bash
# Test your changes
/auto-cdq discovery

# You should see:
# ☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step
#
# Then complete the wizard with arrow keys and Enter
```

---

## Reference Implementation

**autoresearch SKILL.md** (lines 265-299)

Shows exact production pattern:
- Goal | Scope | Metric | Direction (4 sections)
- All in one `AskUserQuestion` call
- Perfect template to copy

---

## Common Mistakes

❌ **"I'll ask all the questions separately"**
→ Use ONE batched call with all questions

❌ **"I'll make 10 sections"**
→ Max 4 per batch (hard CLI limit)

❌ **"I won't give each question a header"**
→ Each question MUST have unique `header`

❌ **"The CLI will handle backward navigation automatically"**
→ You must detect and support revisiting earlier sections

---

## FAQ

**Q: Does this work in all Claude Code environments?**
A: Yes — CLI, Web, Desktop all support this.

**Q: Can I have more than 4 steps?**
A: Use multiple batches. Phase 1 (4 sections), Phase 2 (4 sections), etc.

**Q: Do I need special permissions?**
A: No. Just regroup your questions — that's it.

**Q: Will this break my existing code?**
A: No. This is a pure UX improvement to SKILL.md.

---

## Time Estimate

- **Understand this:** 5 minutes
- **Refactor one workflow:** 1-2 hours
- **Test all workflows:** 1 hour
- **Document:** 30 minutes

Total: **3-4 hours** to implement fully

---

## Start Here

1. **See before/after:** Read `VISUAL_COMPARISON.txt` (5 min)
2. **Understand the why:** Read `SUMMARY_MULTI_SECTION_HEADERS.md` (10 min)
3. **Get step-by-step guide:** Open `GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md`
4. **Reference checklist:** Use `IMPLEMENTATION_CHECKLIST.md`
5. **Test in CLI:** `/auto-cdq discovery`

---

**That's it. Just regroup your questions into batches of 4, and Claude Code's CLI handles the rest.**
