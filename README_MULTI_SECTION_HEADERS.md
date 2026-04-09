# Multi-Section Headers Research & Implementation Guide

## Overview

This is a complete research package on implementing multi-section headers for the auto-cdq wizard, similar to how autoresearch displays its setup wizard.

**Your Question:** Can auto-cdq show all workflow sections (Schema | Table | Preview | Action) left-to-right with ✓/☐ checkmarks and arrow key navigation?

**Answer:** YES. It's built into Claude Code's CLI. This package contains everything you need to implement it.

---

## Quick Start (5 minutes)

1. **Start here:** [`SUMMARY_MULTI_SECTION_HEADERS.md`](SUMMARY_MULTI_SECTION_HEADERS.md)
   - 10-minute read
   - See before/after comparison
   - Understand the core concept
   - No deep technical details

2. **Then see:** [`VISUAL_COMPARISON.txt`](VISUAL_COMPARISON.txt)
   - ASCII art showing the UX difference
   - Code examples (before → after)
   - Clear visual walkthrough

3. **Ready to implement?** → Jump to [`IMPLEMENTATION_CHECKLIST.md`](IMPLEMENTATION_CHECKLIST.md)

---

## Complete Documentation

### For Understanding

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| **SUMMARY_MULTI_SECTION_HEADERS.md** | Quick executive summary | 10 min | Everyone |
| **VISUAL_COMPARISON.txt** | Before/after UI comparison | 5 min | Visual learners |
| **ANALYSIS_MULTI_SECTION_HEADERS.md** | Deep technical analysis | 20 min | Technical leads |

### For Implementation

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| **GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md** | Step-by-step refactoring guide | 30 min | Developers |
| **IMPLEMENTATION_CHECKLIST.md** | Detailed task breakdown | 60 min | Project managers |
| **README_MULTI_SECTION_HEADERS.md** | This index | 5 min | Everyone |

---

## The Concept in One Sentence

**Group your wizard questions (max 4) into a single `AskUserQuestion` call, and Claude Code's CLI automatically renders them as horizontal section headers with checkmarks and arrow key navigation.**

---

## Current State vs. Improved State

### Current (Single Sections)
```
❌ One section at a time
❌ No visual indication of workflow steps
❌ Can't easily revisit earlier choices
❌ Feels like separate questions
```

Example:
```
┌────────────────────┐
│ ☐ Schema          │
│ Which schema...   │
│ 1. samples        │
│ 2. Type something │
└────────────────────┘
```

### Improved (Multi-Section Headers)
```
✅ See all 4 steps at once
✅ Visual progress (☐ → ✓ checkmarks)
✅ Easy backward navigation (← arrow)
✅ Professional wizard experience
```

Example:
```
┌──────────────────────────────────────────────────┐
│ ☐ Schema  ☐ Table  ☐ Preview  ☐ Confirm       │
│ Which schema...                                  │
│ 1. samples                                       │
│ 2. Type something                               │
└──────────────────────────────────────────────────┘
```

---

## Implementation at a Glance

### What Changes

**Before (3 separate calls):**
```python
response1 = AskUserQuestion(questions=[{"header": "Schema", ...}])
response2 = AskUserQuestion(questions=[{"header": "Table", ...}])
response3 = AskUserQuestion(questions=[{"header": "Preview", ...}])
```

**After (1 batched call):**
```python
response = AskUserQuestion(questions=[
    {"header": "Schema", ...},
    {"header": "Table", ...},
    {"header": "Preview", ...},
    {"header": "Confirm", ...}
])
```

### What Stays the Same

- Your backend CDQ logic (no changes needed)
- State management approach (just updated schema)
- API calls and data fetching
- Error handling patterns

### What Claude Code Handles Automatically

- Rendering section headers (☐ Schema | ☐ Table | ...)
- Checkmark updates (☐ → ✓) as user answers
- Arrow key navigation (← →) between sections
- Answer confirmation and modification
- User experience polish

---

## Key Files to Reference

### Source Pattern
- **autoresearch SKILL.md** — Lines 265-299
  - Reference implementation
  - Shows exact pattern used in production
  - Batch question structure

### Claude Code Documentation
- **code.claude.com/docs/en/skills** — Section on AskUserQuestion
  - Explains `header` field behavior
  - Documents multi-question batching
  - Technical details

---

## Workflow Structure Recommendation

```
Phase 1: Workflow Selection
  └─ 1 section: "What workflow?"

Phase 2: Discovery
  └─ 4 sections: Schema | Table | Preview | Next Step

Phase 3: Onboarding
  └─ 4 sections: Dataset Name | Sample Size | Validation | Confirm

Phase 4: Rules
  └─ 4 sections: Analysis | Rules | Testing | Save
```

Each phase is independent — user can complete Discovery, then move to Onboarding, etc.

---

## Step-by-Step Path Forward

### 1. Read (30 minutes total)
- [ ] Read SUMMARY_MULTI_SECTION_HEADERS.md
- [ ] Scan VISUAL_COMPARISON.txt
- [ ] Skim ANALYSIS_MULTI_SECTION_HEADERS.md

### 2. Design (30 minutes)
- [ ] Map out Discovery workflow sections
- [ ] Map out Onboarding workflow sections
- [ ] Map out Rules workflow sections
- [ ] Decide which questions go in each section

### 3. Implement (3-4 hours)
- [ ] Refactor Discovery phase questions into 1 batched call
- [ ] Test in CLI: `/auto-cdq discovery`
- [ ] Refactor Onboarding phase
- [ ] Refactor Rules phase
- [ ] Add backward navigation support

### 4. Test & Document (1-2 hours)
- [ ] Manual CLI testing of all workflows
- [ ] Test arrow key navigation
- [ ] Test backward navigation
- [ ] Update SKILL.md with visual examples

### 5. Deploy
- [ ] Commit changes
- [ ] Create pull request
- [ ] Get code review
- [ ] Merge to main

---

## Success Looks Like

When complete, users running `/auto-cdq discovery` will see:

```
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which schema should we search in?
❯ 1. samples (Recommended)
  2. Type something else
```

After answering, they'll see:

```
✓ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which table would you like to work with?
❯ 1. customers (Recommended)
  2. Search by pattern
```

They can press ← to go back:

```
☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step

Which schema should we search in?
❯ 1. samples (Recommended)  [Can modify]
  2. Type something else
```

---

## Common Questions

**Q: Is this hard to implement?**
A: No. It's just grouping questions differently. The CLI handles all the UI rendering automatically.

**Q: Will this break existing functionality?**
A: No. This is a pure UX improvement. All backend logic stays the same.

**Q: Can I test this before committing?**
A: Yes! Run `/auto-cdq discovery` in CLI and try it. The changes are isolated to SKILL.md and state management.

**Q: What if I have more than 4 steps?**
A: Use multiple batches. Phase 1 shows 4 sections, then Phase 2 shows the next 4 sections.

**Q: Can users still navigate with keyboard only?**
A: Yes! Arrow keys (← →) to navigate, Enter to confirm. No mouse required.

**Q: Will this work on all platforms?**
A: Yes. Claude Code CLI on macOS, Linux, Windows all support this pattern.

---

## Troubleshooting

### Header bar doesn't appear
- Verify you have max 4 questions per `AskUserQuestion` call
- Verify each question has a unique `header` field
- Check Claude Code version (should be recent)

### Navigation keys don't work
- Ensure you're using Claude Code CLI (not VS Code extension)
- Try pressing ← → arrow keys (not left/right in menu)

### Answers not persisting
- Check `.auto-cdq-state.json` schema matches batched response
- Ensure you're updating state after `AskUserQuestion` call

---

## Related Resources

- **autoresearch project:** `/Users/brian/github/autoresearch`
- **autoresearch SKILL.md:** `./.claude/skills/autoresearch/SKILL.md`
- **Claude Code docs:** https://code.claude.com/docs/en/skills
- **auto-cdq current:** `./.claude/skills/auto-cdq/SKILL.md`

---

## Document Map

```
README_MULTI_SECTION_HEADERS.md (this file)
├── SUMMARY_MULTI_SECTION_HEADERS.md ..................... START HERE (executive summary)
├── VISUAL_COMPARISON.txt ............................... See the UX difference
├── ANALYSIS_MULTI_SECTION_HEADERS.md ................... Technical deep dive
├── GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md ......... Step-by-step refactoring
└── IMPLEMENTATION_CHECKLIST.md .......................... Detailed task breakdown
```

---

## Author Notes

This research package contains:
- ✅ Complete analysis of how multi-section headers work in Claude Code
- ✅ Reference to autoresearch's production implementation
- ✅ Step-by-step refactoring guide with code examples
- ✅ Visual before/after comparisons
- ✅ Detailed implementation checklist
- ✅ Updated project memory (MEMORY.md) with findings

All materials created on 2026-04-09.

---

## Get Started Now

**Next action:** Read [`SUMMARY_MULTI_SECTION_HEADERS.md`](SUMMARY_MULTI_SECTION_HEADERS.md) (10 minutes)

Then decide:
- **Learn more:** Read [`ANALYSIS_MULTI_SECTION_HEADERS.md`](ANALYSIS_MULTI_SECTION_HEADERS.md)
- **Ready to code:** Use [`IMPLEMENTATION_CHECKLIST.md`](IMPLEMENTATION_CHECKLIST.md)
- **Need visuals:** See [`VISUAL_COMPARISON.txt`](VISUAL_COMPARISON.txt)

---

*Last updated: April 9, 2026*
