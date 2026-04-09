# Interactive Workflow Pattern — Start Here

**Updated**: 2026-04-09 (Successful reference implementation)

This directory contains everything you need to build interactive `/auto-cdq` style workflows.

---

## What Just Happened (2026-04-09)

A complete interactive workflow was successfully executed:

1. **Discovery** - User found `census_tracts_new_york` table (4,918 rows, 13 columns)
2. **Onboarding** - User registered dataset with DQ job (100% quality score)
3. **Rules** - User created 13 comprehensive quality rules (18 anomalies detected)
4. **Success** - All 13 rules validated and saved

**Pattern Used**: Multi-section headers + AskUserQuestion + skill execution + validation loops

This is now the **REFERENCE IMPLEMENTATION** for all future interactive workflows.

---

## Key Files in This Directory

### 1. Quick Start (Read This First)
- **`QUICK_REFERENCE_INTERACTIVE_PATTERN.md`** ← **START HERE** for implementing new workflows
  - 4-phase template
  - Code patterns (AskUserQuestion, headers, skills)
  - Loop patterns with real examples
  - Testing checklist

### 2. Complete Reference (Full Details)
- **`INTERACTIVE_WORKFLOW_REFERENCE.md`** ← Full 2026-04-09 example
  - Discovery, Onboarding, Rules workflows
  - Success metrics and ratios
  - Implementation patterns (A, B, C, D)
  - Do's and don'ts
  - Copy-paste template

### 3. Mode Distinction (Important!)
- **`INTERACTIVE_VS_NONINTERACTIVE.md`** ← Clear rules
  - Interactive = slash command (user-paced exploration)
  - Non-interactive = direct Python CLI (automated, batch)
  - Key rule: NO slash command args, NO non-interactive via skill
  - Real-world examples for each

### 4. Deep Dive (Theory)
- **`HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md`** ← Pattern theory
  - Architecture details
  - Component breakdown
  - When each pattern works (A, B, C, D)
  - Complete Discovery/Onboarding/Rules examples
  - Evolution notes

---

## Quick Start: Creating Your First Interactive Workflow

### Step 1: Understand the Pattern
```
Read: QUICK_REFERENCE_INTERACTIVE_PATTERN.md (5 min)
```

### Step 2: Copy the Template
```markdown
===================================================================
☐ Phase1    ☐ Phase2    ☐ Phase3    ☐ Phase4
===================================================================

## Phase 1: [Name]
AskUserQuestion → Store selection

## Phase 2: [Name]
Skill execution → Display output → AskUserQuestion
[Validate loop possible]

## Phase 3: [Name]
[For batch ops: Test each item, store results]
AskUserQuestion

## Phase 4: [Name]
Final skill → Display results → Success message
```

### Step 3: Implement Your Workflow
1. Define 3-4 phases
2. Identify where skills execute
3. Plan 1-2 validation loops
4. Write header updates (☐ → ✓)
5. Test end-to-end + error cases

### Step 4: Compare Against Reference
- Check: Does your workflow match the 2026-04-09 pattern?
- Are skills between questions? ✓
- Do headers update? ✓
- Are there validation loops? ✓
- Is raw data displayed? ✓

---

## Key Rules (Must Memorize)

### ✅ DO
1. Insert skills BETWEEN questions
2. Display raw output before asking confirmation
3. Provide loop-back options ("More?", "Different?")
4. Update header after each phase
5. Use lightweight questions (<5 options)
6. Test validation loops thoroughly

### ❌ DON'T
1. Ask all config upfront
2. Hide data output
3. Force linear flow
4. Use heavy surveys
5. Save without testing
6. Use non-interactive mode via slash command

### 🚫 CRITICAL RULE
**NO slash command with CLI arguments**

Wrong: `/auto-cdq discovery --schema samples --table accounts`
Right: `/auto-cdq discovery` then user answers questions

(Non-interactive mode is separate: `python3 .claude/bin/auto-cdq-wizard.py discovery --schema samples`)

---

## Pattern Structure (Copy-Paste)

```
def run_workflow():
    # Header: ☐ Phase1 | ☐ Phase2 | ☐ Phase3 | ☐ Phase4
    
    # Phase 1: Decision
    response = AskUserQuestion(...)  # Ask for user input
    user_selection = response        # Store answer
    # Header: ✓ Phase1 | ☐ Phase2 | ☐ Phase3 | ☐ Phase4
    
    # Phase 2: Data Gathering
    skill_output = run_skill(f"/skill-name --arg {user_selection}")
    display_raw_output(skill_output)        # Show tables/stats
    
    while True:
        response = AskUserQuestion("Looks good?", options=[
            "Yes, proceed",
            "Show more data",
            "Try different",
            "Back"
        ])
        
        if response == "Yes":
            break
        elif response == "Show more":
            skill_output = run_skill(...LIMIT 20)
            display_raw_output(skill_output)
            continue
        elif response == "Try different":
            # Go back to Phase 1
            continue
    # Header: ✓ Phase1 | ✓ Phase2 | ☐ Phase3 | ☐ Phase4
    
    # Phase 3: Validation (if batch)
    test_results = []
    for item in items:
        result = run_skill(f"/test-skill {item}")
        display_result(result)
        test_results.append(result)
    
    response = AskUserQuestion("Save all?", options=...)
    # Header: ✓ Phase1 | ✓ Phase2 | ✓ Phase3 | ☐ Phase4
    
    # Phase 4: Execution
    final_result = run_skill("/final-skill")
    display_success_message(final_result)
    # Header: ✓ Phase1 | ✓ Phase2 | ✓ Phase3 | ✓ Phase4
```

---

## Success Stories

### 2026-04-09: Census Workflow ✅
- **Duration**: 30 minutes
- **Pattern**: Discovery (4 phases) → Onboarding (4 phases) → Rules (4 phases)
- **Skills Executed**: 16+ with data display
- **Validation Loops**: 3 (table selection, data preview, rule testing)
- **Results**: 13 rules created, 100% quality score, 18 anomalies found
- **User Outcome**: Full DQ setup in one session

**This is your reference. Aim for this quality.**

---

## Documentation Structure

```
docs/
├── 00_START_HERE_INTERACTIVE_WORKFLOW.md      ← You are here
├── QUICK_REFERENCE_INTERACTIVE_PATTERN.md     ← Implement template
├── INTERACTIVE_WORKFLOW_REFERENCE.md          ← Full 2026-04-09 example
├── INTERACTIVE_VS_NONINTERACTIVE.md           ← Mode distinction
└── HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md   ← Theory details
```

---

## Next Steps

1. **Read `QUICK_REFERENCE_INTERACTIVE_PATTERN.md`** (15 min)
2. **Review `INTERACTIVE_WORKFLOW_REFERENCE.md`** Discovery phase (10 min)
3. **Implement your workflow** using template
4. **Test against checklist** in Quick Reference
5. **Compare to 2026-04-09 example** for quality

---

## Common Questions

**Q: Should I use this pattern for all interactive workflows?**
A: Yes. The 2026-04-09 example proved it works. Use it for all `/auto-cdq-*` commands.

**Q: Can I skip validation loops?**
A: No. At least one loop per workflow is required. Users need to explore and modify.

**Q: Should slash commands accept CLI args?**
A: No. Never. Slash commands are for interactive workflows. Use direct Python for CLI args.

**Q: How many questions in one AskUserQuestion?**
A: Max 5 options. Lightweight decisions only. Data operations go to skills.

**Q: How many skills per phase?**
A: Usually 1-2. Skills execute between questions. Display output before asking again.

---

## Support

- **Pattern Questions**: See `QUICK_REFERENCE_INTERACTIVE_PATTERN.md`
- **Implementation Help**: See `INTERACTIVE_WORKFLOW_REFERENCE.md`
- **Mode Confusion**: See `INTERACTIVE_VS_NONINTERACTIVE.md`
- **Deep Theory**: See `HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md`

---

**Version**: 2026-04-09 (Validated)
**Authority**: User-driven reference implementation
**Status**: READY FOR DEPLOYMENT

Use this pattern. It works.
