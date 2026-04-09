# Implementation Checklist: Multi-Section Headers for auto-cdq

Use this checklist to guide your refactoring of auto-cdq to use multi-section headers.

---

## Phase 1: Planning & Analysis

- [ ] Read `SUMMARY_MULTI_SECTION_HEADERS.md` — Quick overview
- [ ] Read `ANALYSIS_MULTI_SECTION_HEADERS.md` — Deep technical dive
- [ ] Read `VISUAL_COMPARISON.txt` — See before/after UI
- [ ] Review autoresearch SKILL.md lines 265-299 — Reference pattern
- [ ] Understand: Max 4 questions per `AskUserQuestion` call
- [ ] Understand: Each question's `header` field becomes a visible section
- [ ] Understand: Claude Code CLI handles checkmarks (✓/☐) and navigation automatically

---

## Phase 2: Design Your Workflow Structure

### Discovery Workflow
- [ ] Define sections for Discovery Phase:
  - Section 1: Schema selection
  - Section 2: Table selection  
  - Section 3: Preview confirmation
  - Section 4: Next action (onboarding / rules / exit)
- [ ] Batch these into ONE `AskUserQuestion` call (4 sections)
- [ ] Verify visual order matches user journey (left-to-right)

### Onboarding Workflow
- [ ] Define sections for Onboarding Phase:
  - Section 1: Dataset name configuration
  - Section 2: Sample size selection
  - Section 3: Validation confirmation
  - Section 4: Confirm & proceed
- [ ] Batch these into ONE `AskUserQuestion` call (4 sections)

### Rules Workflow
- [ ] Define sections for Rules Phase:
  - Section 1: Column analysis
  - Section 2: Rule selection
  - Section 3: Rule testing/confirmation
  - Section 4: Save rules
- [ ] Batch these into ONE `AskUserQuestion` call (4 sections)

---

## Phase 3: Code Refactoring

### Update `.auto-cdq-state.json` Schema
- [ ] Add fields to track which workflow is active
- [ ] Add fields for each batch's answers
- [ ] Example:
  ```json
  {
    "workflow": null,
    "discovery": {
      "schema": null,
      "table": null,
      "preview_confirmed": false,
      "next_action": null
    },
    "onboarding": {
      "dataset_name": null,
      "sample_size": null,
      "validated": false
    }
  }
  ```

### Refactor Discovery Workflow
- [ ] Combine current 4 separate questions into 1 batched call
- [ ] Create single `AskUserQuestion` with:
  - Question 1: "Which schema..." → header: "Schema"
  - Question 2: "Which table..." → header: "Table"
  - Question 3: "Preview OK..." → header: "Preview"
  - Question 4: "What next..." → header: "Next Step"
- [ ] Extract answers from batched response:
  ```python
  response = AskUserQuestion(questions=[...])
  schema = response["Which schema should we search in?"]
  table = response["Which table would you like to work with?"]
  # etc.
  ```
- [ ] Update state tracking
- [ ] Remove old separate question calls

### Refactor Onboarding Workflow
- [ ] Same as Discovery: combine into 1 batched call
- [ ] Create 4 questions for the 4 sections
- [ ] Extract answers and update state

### Refactor Rules Workflow
- [ ] Same as Discovery: combine into 1 batched call
- [ ] Create 4 questions for the 4 sections
- [ ] Extract answers and update state

### Add Backward Navigation Support
- [ ] Detect if user wants to revisit earlier phase
- [ ] When user navigates backward, re-display that phase's questions
- [ ] Pre-populate earlier answers so user sees current selections
- [ ] Allow modification of earlier choices

---

## Phase 4: Testing

### Manual CLI Testing
- [ ] Run `/auto-cdq discovery` in Claude Code terminal
- [ ] Verify header bar appears with all 4 sections:
  ```
  ☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step
  ```
- [ ] Answer first question (Schema)
- [ ] Verify cursor moves to next question
- [ ] Verify first section now shows ✓:
  ```
  ✓ Schema    ☐ Table    ☐ Preview    ☐ Next Step
  ```
- [ ] Test arrow key navigation:
  - [ ] Press → to move forward through sections
  - [ ] Press ← to go back to previous section
- [ ] Test answer modification:
  - [ ] Navigate back to Schema with ←
  - [ ] Change the answer
  - [ ] Verify it updates

### Navigation Edge Cases
- [ ] Test at first question (← should have no effect)
- [ ] Test at last question (→ should have no effect)
- [ ] Test rapid navigation (← → → ←)
- [ ] Test changing answer while navigating backward

### Workflow Completeness
- [ ] Complete full Discovery phase → verify all 4 ✓
- [ ] Move to Onboarding → verify state persists
- [ ] Navigate between phases → verify no data loss
- [ ] Test "Exit" option → verify clean state reset

### Edge Cases
- [ ] User types something else → verify custom input handling
- [ ] User selects "Chat about this" → verify fallback behavior
- [ ] Network/API errors → verify error handling with headers visible

---

## Phase 5: Documentation

### Update auto-cdq SKILL.md
- [ ] Document the multi-section header pattern in intro
- [ ] Show visual example of Discovery phase with headers:
  ```
  ☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step
  ```
- [ ] Add keyboard navigation hints:
  - Use ← → to navigate between sections
  - Press Enter to confirm answer
  - Press Escape to go back to menu (if supported)
- [ ] Update each workflow section to explain new batched structure
- [ ] Add note about backward navigation support

### Create Visual Examples
- [ ] Screenshot or ASCII art showing:
  - Initial state (☐ ☐ ☐ ☐)
  - After first answer (✓ ☐ ☐ ☐)
  - After navigating backward (☐ ☐ ☐ ☐ — cursor back at first)
- [ ] Add to SKILL.md or separate visual guide

### Update README or docs/
- [ ] Document the improved UX in project README
- [ ] Mention arrow key navigation feature
- [ ] Link to detailed guide (GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md)

---

## Phase 6: Performance & Polish

### Code Quality
- [ ] Remove dead code (old separate question calls)
- [ ] Verify no duplicate state tracking
- [ ] Clean up temporary debug logging
- [ ] Ensure consistent naming conventions

### State Management
- [ ] Verify `.auto-cdq-state.json` is updated after each batch
- [ ] Test state persistence across phase boundaries
- [ ] Verify state is cleared on Exit

### Error Handling
- [ ] Graceful handling of API errors (display headers even on error)
- [ ] User-friendly error messages
- [ ] Recovery options (Retry / Go Back / Exit)

---

## Phase 7: Final Testing & Deployment

### Full Workflow Test
- [ ] Run `/auto-cdq discovery` → complete full Discovery phase
- [ ] Verify → run `/auto-cdq onboarding` → complete Onboarding phase
- [ ] Verify → run `/auto-cdq rules` → complete Rules phase
- [ ] Verify state across all phases

### Cross-Workflow Test
- [ ] Start Discovery, navigate to Onboarding → state persists
- [ ] Start Onboarding, go back to previous phase → data retained
- [ ] Exit and restart → state clears properly

### Performance
- [ ] Verify CLI response time is acceptable
- [ ] Check for lag in navigation (← →)
- [ ] Verify header bar renders immediately

---

## Success Criteria

✅ **Discovery Phase shows:** `☐ Schema    ☐ Table    ☐ Preview    ☐ Next Step`

✅ **Checkmarks appear:** As each section is completed (`☐` → `✓`)

✅ **Navigation works:** Arrow keys (← →) move between sections

✅ **Backward nav works:** Can revisit earlier sections and modify answers

✅ **No data loss:** State persists across navigation and phases

✅ **Professional UX:** Feels like cohesive wizard, not separate questions

✅ **Documentation complete:** SKILL.md updated with examples

---

## Files to Modify

- [ ] `.claude/skills/auto-cdq/SKILL.md` — Main refactoring
- [ ] `.auto-cdq-state.json` — State schema update
- [ ] `docs/auto-cdq/GUIDE.md` (if exists) — Update with new UX
- [ ] `README.md` — Optional mention of improved UX

---

## Files Already Created (Reference)

- `SUMMARY_MULTI_SECTION_HEADERS.md` — Quick reference
- `ANALYSIS_MULTI_SECTION_HEADERS.md` — Technical deep dive
- `GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md` — Step-by-step refactoring
- `VISUAL_COMPARISON.txt` — Before/after UI comparison
- `IMPLEMENTATION_CHECKLIST.md` — This file

---

## Estimated Effort

- **Analysis & Design:** 1-2 hours (mostly done via research above)
- **Code Refactoring:** 2-3 hours (batching questions, state management)
- **Testing:** 1-2 hours (manual CLI testing, edge cases)
- **Documentation:** 30-60 minutes (SKILL.md updates)
- **Total:** 5-8 hours of focused work

---

## Next Steps

1. **Review the reference materials** — Especially VISUAL_COMPARISON.txt for clarity
2. **Start with Discovery phase** — Most complex, sets pattern for others
3. **Test incrementally** — Complete one phase before moving to next
4. **Get user feedback** — Test with actual `/auto-cdq discovery` run
5. **Document as you go** — Update SKILL.md with examples

---

## Questions or Blockers?

If you hit issues during implementation:
- Check GUIDE_IMPLEMENTING_MULTI_SECTION_HEADERS.md for code examples
- Refer to autoresearch SKILL.md (lines 265-299) for reference pattern
- Review ANALYSIS_MULTI_SECTION_HEADERS.md for technical details
- Test in isolation (single batched question) before full workflow
