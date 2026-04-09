# CDQ Wizard Documentation Index

Complete guide to building interactive CDQ workflows using the **Hybrid Progressive Disclosure Pattern**.

---

## 📚 Documentation Structure

### Core Pattern Documentation

1. **[HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md](./HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md)**
   - What is the pattern?
   - Why use it?
   - Core components
   - Four workflow patterns
   - Best practices
   - Error handling
   - Performance considerations

### Implementation Guides

2. **[IMPLEMENTING_NEW_WORKFLOWS.md](./IMPLEMENTING_NEW_WORKFLOWS.md)**
   - Step-by-step guide to apply pattern
   - Planning phase (define goal, structure)
   - Design phase (sketch flow, document decisions)
   - Code phase (implement in Python)
   - Testing checklist
   - Complete example walkthrough
   - Troubleshooting tips
   - Copy-paste template

### Real-World Examples

3. **[DISCOVERY_WORKFLOW_EXAMPLE.md](./DISCOVERY_WORKFLOW_EXAMPLE.md)**
   - Complete Discovery workflow implementation
   - Schema selection (lightweight)
   - Table search with results (interactive)
   - Preview with validation loop (high interaction)
   - Multi-section header tracking

4. **[ONBOARDING_WORKFLOW_EXAMPLE.md](./ONBOARDING_WORKFLOW_EXAMPLE.md)**
   - Complete Onboarding workflow implementation
   - Dataset configuration
   - Sample size selection with row count
   - Connection testing
   - Job execution and results display

5. **[RULES_WORKFLOW_EXAMPLE.md](./RULES_WORKFLOW_EXAMPLE.md)**
   - Complete Rules workflow implementation
   - Data analysis and rule suggestion
   - Rule type selection
   - Per-rule testing validation loop
   - Batch save workflow

6. **[ALERTS_WORKFLOW_EXAMPLE.md](./ALERTS_WORKFLOW_EXAMPLE.md)**
   - Complete Alerts workflow implementation
   - Rule selection from dataset
   - Alert configuration (threshold, channels, recipients)
   - Alert condition testing with SQL
   - Save and activation

---

## 🎯 Quick Start

### For Understanding the Pattern
1. Start: [HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md](./HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md)
2. Read: "Overview" section
3. Look at: "Implementation Pattern" with visual diagram
4. Learn: "Four Workflow Patterns" section

**Time: 10-15 minutes**

### For Building a New Workflow
1. Read: [IMPLEMENTING_NEW_WORKFLOWS.md](./IMPLEMENTING_NEW_WORKFLOWS.md)
2. Follow: "Phase 1: Plan Your Workflow"
3. Follow: "Phase 2: Design the Structure"
4. Copy: Template at end of guide
5. Modify: For your specific workflow

**Time: 30-45 minutes for first workflow**

### For Implementing Alerts (Example)
1. Read: [ALERTS_WORKFLOW_EXAMPLE.md](./ALERTS_WORKFLOW_EXAMPLE.md)
2. Study: Phase descriptions (1-4)
3. Review: Code template at end
4. Apply: Same pattern to your workflow

**Time: 20-30 minutes**

---

## 📋 Workflow Comparison

| Workflow | Phases | Key Skill Calls | Complexity | Best For |
|----------|--------|-----------------|-----------|----------|
| **Discovery** | 4 | search tables, preview SQL | Medium | Finding & previewing data |
| **Onboarding** | 4 | row count, test connection, run job | Medium | Dataset registration |
| **Rules** | 4 | analyze, test each, save batch | High | Complex rule validation |
| **Alerts** | 4 | get rules, test condition, save | Medium | Alert configuration |
| **Schedule** | 4 | search dataset, configure, save | Low | Simple configuration |

---

## 🏗️ Pattern Components

### 1. Multi-Section Headers
```
☐ Phase 1    ☐ Phase 2    ☐ Phase 3    ☐ Phase 4
```
Updates as user progresses:
```
✓ Phase 1    ✓ Phase 2    ☐ Phase 3    ☐ Phase 4
```

### 2. Lightweight Decisions
Simple AskUserQuestion calls, no skill execution
- Example: "Which schema?" or "Confirm?"

### 3. Heavy Operations
Skill execution with result display
- Example: Run `cdq-list-tables` → Show results table

### 4. Validation Loops
User gives feedback, can modify and retry
- Example: Preview data → "More rows?" → "Different table?"

### 5. Batch Operations
Test multiple items, validate each, batch save
- Example: Analyze 10 rules, test each, save all

---

## 🎓 Learning Path

### Level 1: Understand the Pattern (1-2 hours)
- [ ] Read HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md
- [ ] Study visual diagrams
- [ ] Understand the 4 components
- [ ] Review best practices

### Level 2: Study Examples (1-2 hours)
- [ ] Read Discovery workflow example
- [ ] Read Onboarding workflow example
- [ ] Identify pattern components in each
- [ ] Note similarities and differences

### Level 3: Plan Your Workflow (30-45 min)
- [ ] Define your goal
- [ ] Identify key decisions
- [ ] List skills to use
- [ ] Sketch 3-4 phases
- [ ] Document interaction types

### Level 4: Implement & Test (1-3 hours)
- [ ] Use IMPLEMENTING_NEW_WORKFLOWS.md
- [ ] Build main workflow function
- [ ] Add helper functions
- [ ] Test end-to-end
- [ ] Test error cases

### Level 5: Polish & Validate (30-60 min)
- [ ] Review UX (is it clear?)
- [ ] Add error handling
- [ ] Test edge cases
- [ ] Get user feedback

---

## 📊 Real-World Workflows

### Discovery Workflow (Implemented ✓)
**Goal:** Find and preview a table

**Key Interaction:**
```
Schema selection → Table search (interactive) → Preview (validation loop) → Route
```

**Status:** Complete, tested, in production

### Onboarding Workflow (Implemented ✓)
**Goal:** Register dataset and run initial DQ job

**Key Interaction:**
```
Name dataset → Check row count → Test connection → Run job → Show results
```

**Status:** Complete, tested, in production

### Rules Workflow (Implemented ✓)
**Goal:** Create and validate data quality rules

**Key Interaction:**
```
Analyze → Select rules → Test each rule (loop) → Batch save → Verify
```

**Status:** Complete, tested, in production

### Alerts Workflow (Documented)
**Goal:** Create alerts for DQ violations

**Key Interaction:**
```
Select rule → Configure alert → Test condition → Confirm → Save
```

**Status:** Documented, ready to implement

### Schedule Workflow (Example in guide)
**Goal:** Schedule recurring DQ jobs

**Key Interaction:**
```
Select dataset → Choose frequency → Pick time → Confirm → Create
```

**Status:** Template provided in guide

---

## 🚀 Implementation Patterns

### Pattern A: Simple Selection
**When:** Straightforward choices, no validation needed
**Phases:** ~3 lightweight questions
**Skills:** Minimal
**Example:** Schedule DQ job (select dataset, frequency, time)

### Pattern B: Search + Results
**When:** User searches for something, needs to pick from results
**Phases:** Ask term → Run search → Show results → Pick
**Skills:** 1-2 search/list skills
**Example:** Discovery workflow table search

### Pattern C: Preview + Validation
**When:** User needs to see actual data before confirming
**Phases:** Configure → Run → Display → Validate (loop)
**Skills:** 2-3 execution skills
**Example:** Onboarding with row count check

### Pattern D: Batch Operations
**When:** Multiple items to test/validate before batch save
**Phases:** Analyze → Select → Test each → Batch save
**Skills:** 3-4 analysis/test/save skills
**Example:** Rules workflow with per-rule testing

---

## 🛠️ Tools & Resources

### Files to Reference
- `lib/client.py` - All available CDQ skills
- `.Claude.md` (project) - Environment setup
- `.env.example` - Configuration template

### Helper Functions Needed
- `print_header(phases)` - Display multi-section header
- `update_header(phases)` - Refresh header with new state
- `print_results_table(data)` - Format results nicely
- `print_skill_execution(name, args)` - Show skill running
- `handle_validation_loop(result)` - Manage "retry/modify/accept" feedback

### Skills Available
See `lib/client.py` for:
- Data exploration: `cdq-list-tables`, `cdq-search-catalog`, `cdq-run-sql`
- Job management: `cdq-run-dq-job`, `cdq-get-results`, `cdq-get-jobs`
- Rule management: `cdq-get-rules`, `cdq-save-rule`, `cdq-workflow-suggest-rules`
- Alert management: `cdq-get-alerts`, `cdq-save-alert`
- Validation: `cdq-test-connection`

---

## ✅ Quality Checklist

### Design Phase
- [ ] Goal is clear and specific
- [ ] All key decisions identified
- [ ] Skills mapped to workflow phases
- [ ] 3-4 phases defined
- [ ] Interaction types assigned to each phase

### Implementation Phase
- [ ] Main workflow function created
- [ ] Helper functions implemented
- [ ] All skills called at right points
- [ ] All outputs displayed properly
- [ ] Error handling added

### Testing Phase
- [ ] Full end-to-end flow works
- [ ] Header updates correctly
- [ ] Skill outputs display properly
- [ ] Validation loops work
- [ ] Error cases handled
- [ ] Edge cases tested

### Polish Phase
- [ ] UX is clear (user knows what to do)
- [ ] Messages are professional
- [ ] Output is readable (tables, formatting)
- [ ] Performance is acceptable
- [ ] Feedback received from users

---

## 📞 Support & Troubleshooting

### Common Issues

**Header Not Updating**
- Solution: Call `update_header(phases)` after phase complete
- Reference: HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md → "Header Management"

**Skill Not Running**
- Solution: Check skill name and arguments format
- Reference: `lib/client.py` for correct skill naming

**Results Not Displaying**
- Solution: Add `print_results(result)` after skill execution
- Reference: IMPLEMENTING_NEW_WORKFLOWS.md → "Step 3.1: Create Helper Functions"

**Validation Loop Infinite**
- Solution: Provide clear "Cancel" option to exit
- Reference: HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md → "Validation Loops"

**Slow Performance**
- Solution: Add LIMIT clauses, show progress
- Reference: HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md → "Performance Considerations"

---

## 📖 Additional Reading

- Hybrid UX patterns (general)
- Progressive disclosure in UI design
- Validation loop best practices
- Error handling strategies
- Terminal UI design

---

## 🔗 Cross-References

### By Skill
- `cdq-list-tables` → Discovery, Schedule workflows
- `cdq-run-sql` → All workflows (testing/preview)
- `cdq-run-dq-job` → Onboarding, Schedule workflows
- `cdq-workflow-suggest-rules` → Rules workflow
- `cdq-save-rule` → Rules workflow
- `cdq-save-alert` → Alerts workflow

### By Phase Type
- Lightweight selection → Discovery (schema), Onboarding (name), Alerts (rule)
- Interactive selection → Discovery (table), Alerts (alert config)
- Validation loop → Discovery (preview), Rules (per-rule), Alerts (test)
- Batch operations → Rules (test all, save all)

### By Interaction Pattern
- Search + results → DISCOVERY_WORKFLOW_EXAMPLE.md Phase 2
- Config + validation → ONBOARDING_WORKFLOW_EXAMPLE.md Phase 3
- Analyze + test each → RULES_WORKFLOW_EXAMPLE.md Phase 3
- Test condition → ALERTS_WORKFLOW_EXAMPLE.md Phase 3

---

## 🎯 Next Steps

### To Build Discovery Workflow
→ Read: `DISCOVERY_WORKFLOW_EXAMPLE.md`

### To Build Alerts Workflow
→ Read: `ALERTS_WORKFLOW_EXAMPLE.md`

### To Build Your Own Workflow
→ Read: `IMPLEMENTING_NEW_WORKFLOWS.md`

### To Understand Pattern Deeply
→ Read: `HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md`

---

Last updated: 2025-04-09
Pattern validated: ✓ Discovery, ✓ Onboarding, ✓ Rules workflows tested and in production

