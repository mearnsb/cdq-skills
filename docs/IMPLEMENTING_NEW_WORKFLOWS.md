# Implementing New Workflows with Hybrid Progressive Disclosure

**Step-by-step guide** to apply the hybrid pattern to any CDQ workflow.

---

## Phase 1: Plan Your Workflow

### Step 1.1: Define the Goal

Answer: **What should the user accomplish?**

Examples:
- "Discover and preview a table"
- "Create data quality rules"
- "Set up alerts for violations"
- "Configure data remediation"
- "Schedule recurring quality jobs"

**Your goal:**
```
Goal: [Your workflow goal here]

Expected outcome: [What user should have when done]
```

### Step 1.2: Identify Key Decisions

What choices does the user need to make?

Examples:
- "Which schema to explore?"
- "Which rule type to enable?"
- "How often to run the job?"

Break into categories:
- **Configuration choices** (simple questions)
- **Selection choices** (need to show options)
- **Approval/confirmation** (yes/no decisions)

**Your decisions:**
```
Configuration:
  - [Decision 1]
  - [Decision 2]

Selection:
  - [Decision 3]
  - [Decision 4]

Approvals:
  - [Decision 5]
```

### Step 1.3: Identify Skills to Use

Which existing CDQ skills support this workflow?

Available skills:
- `cdq-search-catalog` - Search for datasets
- `cdq-list-tables` - List available tables
- `cdq-run-sql` - Execute SQL queries
- `cdq-test-connection` - Test API connection
- `cdq-run-dq-job` - Register and run DQ job
- `cdq-get-rules` - List rules for dataset
- `cdq-save-rule` - Create a rule
- `cdq-get-results` - Get job results
- `cdq-save-alert` - Create an alert
- `cdq-workflow-suggest-rules` - Analyze and suggest rules

**Your skills:**
```
Phase 1: [Skill 1], [Skill 2]
Phase 2: [Skill 3]
Phase 3: [Skill 4], [Skill 5]
Phase 4: [Skill 6]
```

### Step 1.4: Design Header Phases

Group decisions into 3-4 logical phases.

**Rule:** Each phase represents one major section of the journey.

Examples:

```
Discovery Workflow:
  Phase 1: Schema (selection)
  Phase 2: Table (search + pick)
  Phase 3: Preview (validation)
  Phase 4: Next Step (routing)

Onboarding Workflow:
  Phase 1: Name (config)
  Phase 2: Size (selection)
  Phase 3: Validate (testing)
  Phase 4: Run (execution)

Rules Workflow:
  Phase 1: Options (analysis)
  Phase 2: Select (selection)
  Phase 3: Test (validation loop)
  Phase 4: Save (execution)

Alerts Workflow:
  Phase 1: Rule (selection)
  Phase 2: Config (configuration)
  Phase 3: Test (validation)
  Phase 4: Save (execution)
```

**Your phases:**
```
Header: ☐ [Phase 1]    ☐ [Phase 2]    ☐ [Phase 3]    ☐ [Phase 4]

Phase 1: [Name] - [Description]
Phase 2: [Name] - [Description]
Phase 3: [Name] - [Description]
Phase 4: [Name] - [Description]
```

### Step 1.5: Identify Which Phases Need Interaction

For each phase, decide: **Lightweight question OR Heavy operation?**

| Phase | Type | Skills Used | Interaction |
|-------|------|------------|-------------|
| Phase 1 | Lightweight? | None | Just ask question |
| Phase 2 | Heavy? | cdq-list-tables | Ask term → Run → Show results → Ask pick |
| Phase 3 | Heavy? | cdq-run-sql | Run test → Show output → Ask validation |
| Phase 4 | Lightweight? | cdq-save-rule | Just confirm |

**Your interaction matrix:**
```
Phase 1 [Lightweight / Heavy]:
  Skill(s): [List]
  User input: [Question type]
  Skill output: [Display type]
  Loop back? [Yes/No]

Phase 2 [Lightweight / Heavy]:
  ...
```

---

## Phase 2: Design the Structure

### Step 2.1: Sketch the Flow

For each phase, draw what happens:

```
PHASE 1: [Phase Name]
─────────────────────────────────────────
  [Lightweight: Just question]
  └─ Ask → Answer → Mark ✓

  OR

  [Heavy: Question + Skill + Result + Validation]
  ├─ Ask for input (search term)
  ├─ Run Skill → Display results
  ├─ Ask for selection (pick from results)
  └─ Mark ✓

PHASE 2: [Phase Name]
─────────────────────────────────────────
  [Instructions for Phase 2]
  ├─ Step 1
  ├─ Step 2
  └─ Step 3

...repeat...
```

### Step 2.2: Document Each Question

For every AskUserQuestion in your workflow:

```python
{
    "question": "Your question text?",
    "header": "Phase X: Name",
    "multiSelect": False,  # or True
    "options": [
        {
            "label": "Option 1",
            "description": "What this means"
        },
        ...
    ]
}
```

**Example for your workflow:**

```
Phase 1 - Question 1:
  Text: "Which schema should we search in?"
  Header: "Schema"
  Type: Single select
  Options:
    - samples (default)
    - public
    - other

Phase 1 - Question 2 (if needed):
  Text: "Ready to proceed?"
  Header: "Confirm"
  Type: Single select
  Options:
    - Yes
    - No
```

### Step 2.3: Document Each Skill Call

For every skill you'll run:

```python
Skill: cdq-list-tables
Args: --schema {schema_var} --search {search_term}
When: Between Q1 and Q2
Display: Results table with columns [name, row_count, status]
Error: If no results → Ask "different search term?"
```

**Example for your workflow:**

```
Skill 1: [Name]
  Args: [Arguments]
  When: After [Phase X Question Y]
  Display: [How to show results]
  Loop? [If user says "more", run again with modified args]

Skill 2: [Name]
  ...
```

### Step 2.4: Design Validation Loops

For phases with validation, document the loop:

```
User sees: [Result]
Question: [Validation question]
Options:
  - "Accept" → Mark complete, move forward
  - "Modify" → [What changes] → Run skill again → Back to "User sees"
  - "Different" → [Go back to earlier phase]
```

**Example:**

```
User sees: SQL preview results (5 rows)
Question: "Does this data look right?"
Options:
  - "Yes, use it" → Mark ✓, continue
  - "Show more rows" → Run cdq-run-sql with LIMIT 20 → Loop
  - "Different table" → Back to table selection phase
```

---

## Phase 3: Code Structure

### Step 3.1: Create Helper Functions

```python
def print_header(phases):
    """Print multi-section header with checkmarks"""
    header = " ".join([
        f"{'✓' if s['complete'] else '☐'} {s['name']}"
        for s in phases
    ])
    print(f"\n{'═' * 80}")
    print(header)
    print(f"{'═' * 80}\n")

def print_section_complete(phase_name):
    """Print phase completion message"""
    print(f"\n{phase_name} COMPLETE ✓\n")

def update_header(phases):
    """Reprint header with updated status"""
    print_header(phases)

def print_results_table(data, columns):
    """Print formatted results table"""
    # Use markdown tables or ASCII art
    pass

def print_skill_execution(skill_name, args):
    """Print skill execution status"""
    print(f"\n🔄 [RUNNING SKILL: {skill_name} {args}]\n")

def handle_validation_loop(result, question_text):
    """Handle validation loop with user feedback"""
    while True:
        print_result(result)
        feedback = ask_validation_question(question_text)
        if feedback == "accept":
            return True
        elif feedback == "modify":
            result = rerun_with_modifications(result)
        elif feedback == "back":
            return False
```

### Step 3.2: Main Workflow Function

```python
def run_your_workflow():
    """Main workflow using hybrid pattern"""

    # Initialize state
    phases = [
        {"name": "Phase 1", "complete": False},
        {"name": "Phase 2", "complete": False},
        {"name": "Phase 3", "complete": False},
        {"name": "Phase 4", "complete": False},
    ]

    # Print initial header
    print_header(phases)

    # PHASE 1
    print("\n[PHASE 1: Phase 1 Name]\n")

    # Ask question
    response1 = ask_user_question(...)
    value1 = extract_answer(response1)

    # Mark complete
    phases[0]["complete"] = True
    update_header(phases)

    # PHASE 2
    print("\n[PHASE 2: Phase 2 Name]\n")

    # Ask for input
    response2a = ask_user_question(...)
    search_term = extract_answer(response2a)

    # Run skill
    print_skill_execution("cdq-skill-name", f"--arg {search_term}")
    results = run_skill("cdq-skill-name", f"--arg {search_term}")
    print_results_table(results)

    # Ask for selection
    response2b = ask_user_question(...)
    value2 = extract_answer(response2b)

    # Mark complete
    phases[1]["complete"] = True
    update_header(phases)

    # PHASE 3
    print("\n[PHASE 3: Phase 3 Name]\n")

    # Validation loop
    while not validated:
        # Run skill
        result = run_skill(...)
        print_result(result)

        # Ask validation
        feedback = ask_validation_question(...)
        if feedback == "yes":
            validated = True
        elif feedback == "more":
            # Rerun with modifications
            pass
        elif feedback == "back":
            # Go to Phase 2
            return run_your_workflow()

    # Mark complete
    phases[2]["complete"] = True
    update_header(phases)

    # PHASE 4
    print("\n[PHASE 4: Phase 4 Name]\n")

    # Final confirmation
    response4 = ask_user_question(...)
    proceed = extract_answer(response4)

    if not proceed:
        return "Cancelled"

    # Final action
    result = run_skill(...)

    # Mark complete
    phases[3]["complete"] = True
    update_header(phases)

    print("\n✅ Workflow complete!")
    return result
```

### Step 3.3: Error Handling

```python
def run_phase_with_error_handling(phase_name, phase_function):
    """Run a phase with error handling"""
    try:
        return phase_function()
    except ConnectionError as e:
        print(f"❌ {phase_name}: Connection failed")
        print(f"   {str(e)}")
        response = ask_user_question(
            "What would you like to do?",
            ["Retry", "Go back", "Cancel"]
        )
        if response == "Retry":
            return run_phase_with_error_handling(phase_name, phase_function)
        elif response == "Go back":
            return None  # Return to previous phase
        else:
            return "Cancelled"
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return "Error"
```

---

## Phase 4: Testing Checklist

### Basic Functionality
- [ ] Full workflow completes without errors
- [ ] All phases execute in order
- [ ] Header updates correctly after each phase
- [ ] Final result is correct

### Skill Integration
- [ ] Each skill executes correctly
- [ ] Skill output displays properly
- [ ] Errors from skills are handled
- [ ] Skills receive correct arguments

### User Experience
- [ ] Header is always visible and current
- [ ] Questions are clear and well-formatted
- [ ] Results display readably
- [ ] Options are obviously actionable

### Validation Loops (if applicable)
- [ ] User can loop back ("More rows", "Modify", etc.)
- [ ] Loop state is maintained correctly
- [ ] Can loop multiple times
- [ ] Can exit loop and proceed

### Error Cases
- [ ] No results from skill (handled gracefully)
- [ ] API connection fails (error message + recovery)
- [ ] User cancels (clean exit)
- [ ] Invalid user input (clear error)

### Edge Cases
- [ ] Large result sets (paginate or truncate)
- [ ] Empty result sets (clear message)
- [ ] Very long running skills (progress indicator)
- [ ] Multiple workflows (state isolation)

---

## Phase 5: Example: Implementing "Schedule DQ Job" Workflow

Let me walk through a complete example to show how the pattern applies.

### Planning Phase

**Goal:**
"Allow users to schedule recurring DQ jobs with a wizard"

**Key Decisions:**
1. Which dataset? (selection)
2. How often? (configuration)
3. What time? (configuration)
4. Confirm? (approval)

**Skills to Use:**
- `cdq-search-catalog` - Find dataset
- `cdq-run-dq-job` - Create schedule

**Header Phases:**
```
☐ Dataset    ☐ Frequency    ☐ Time    ☐ Confirm
```

### Design Phase

**Phase 1: Dataset Selection**
- Type: Lightweight
- Ask: "Which dataset?"
- Skill: cdq-search-catalog
- Display: Dataset list
- Action: Pick from list

**Phase 2: Schedule Frequency**
- Type: Lightweight
- Ask: "How often?"
- Options: Daily, Weekly, Monthly
- No skill needed

**Phase 3: Time Configuration**
- Type: Lightweight
- Ask: "What time?"
- Options: 12am UTC, 6am UTC, 6pm UTC
- Show: "Job will run at [time] every [frequency]"

**Phase 4: Confirmation**
- Type: Decision
- Show: Full schedule config
- Skill: cdq-run-dq-job (with schedule)
- Confirm: Yes/No

### Code Phase

```python
def run_schedule_workflow():
    phases = [
        {"name": "Dataset", "complete": False},
        {"name": "Frequency", "complete": False},
        {"name": "Time", "complete": False},
        {"name": "Confirm", "complete": False},
    ]
    print_header(phases)

    # Phase 1: Dataset
    response = ask_user_question("Which dataset?", [...])
    dataset = response[...]
    phases[0]["complete"] = True
    update_header(phases)

    # Phase 2: Frequency
    response = ask_user_question("How often?", [
        ("daily", "Every day"),
        ("weekly", "Every week"),
        ("monthly", "Every month")
    ])
    frequency = response[...]
    phases[1]["complete"] = True
    update_header(phases)

    # Phase 3: Time
    response = ask_user_question("What time?", [
        ("0", "12am UTC"),
        ("6", "6am UTC"),
        ("18", "6pm UTC")
    ])
    time = response[...]

    # Show impact
    print(f"\nSchedule preview:")
    print(f"  Dataset: {dataset}")
    print(f"  Frequency: {frequency}")
    print(f"  Time: {time}:00 UTC")

    phases[2]["complete"] = True
    update_header(phases)

    # Phase 4: Confirm
    response = ask_user_question("Create schedule?", [
        ("yes", "Yes, create"),
        ("no", "No, cancel")
    ])

    if response == "no":
        return "Cancelled"

    # Execute
    print("🔄 [RUNNING SKILL: cdq-run-dq-job with schedule]")
    result = run_skill("cdq-run-dq-job",
        f"--dataset '{dataset}' --schedule '{frequency}' --time '{time}'"
    )

    phases[3]["complete"] = True
    update_header(phases)

    print(f"\n✅ Schedule created!")
    return result
```

---

## Best Practices Summary

### Design
✅ Keep headers consistent (3-4 phases max)
✅ Identify skill execution points upfront
✅ Plan validation loops where data impacts decisions
✅ Use lightweight questions for pure config
✅ Use heavy operations when data informs next decision

### Implementation
✅ Create helper functions for common operations
✅ Handle errors at skill boundary
✅ Display raw output (SQL, results, metrics)
✅ Provide clear loop-back options
✅ Update header after each major step

### Testing
✅ Test full path end-to-end
✅ Test error cases (no results, API failures)
✅ Test validation loops (multiple iterations)
✅ Test edge cases (large results, long operations)

---

## Troubleshooting

### Header Not Updating
**Problem:** Header shows old state after phase complete
**Solution:** Call `update_header(phases)` after marking phase complete

### Skill Not Displaying Output
**Problem:** Skill runs but results don't show
**Solution:** Add `print_results(result)` after skill execution

### Validation Loop Infinite
**Problem:** User can't escape loop
**Solution:** Add "Cancel" option that breaks out of loop

### Large Results Unreadable
**Problem:** Too much output floods screen
**Solution:** Use pagination or truncation (show first 10, ask for more)

---

## References

- `docs/HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md` - Full pattern guide
- `docs/DISCOVERY_WORKFLOW_EXAMPLE.md` - Discovery workflow
- `docs/ONBOARDING_WORKFLOW_EXAMPLE.md` - Onboarding workflow
- `docs/RULES_WORKFLOW_EXAMPLE.md` - Rules workflow
- `docs/ALERTS_WORKFLOW_EXAMPLE.md` - Alerts workflow
- `lib/client.py` - Available skills reference

---

## Template: Copy & Paste Starter

```python
def run_my_new_workflow():
    """New workflow using hybrid pattern"""

    # SETUP
    phases = [
        {"name": "Phase 1 Name", "complete": False},
        {"name": "Phase 2 Name", "complete": False},
        {"name": "Phase 3 Name", "complete": False},
        {"name": "Phase 4 Name", "complete": False},
    ]
    print_header(phases)

    # PHASE 1
    print("\n[PHASE 1: Description]\n")
    response = ask_user_question(...)
    result1 = extract_answer(response)
    phases[0]["complete"] = True
    update_header(phases)

    # PHASE 2
    print("\n[PHASE 2: Description]\n")
    response = ask_user_question(...)
    result2 = extract_answer(response)
    phases[1]["complete"] = True
    update_header(phases)

    # PHASE 3
    print("\n[PHASE 3: Description]\n")
    print_skill_execution("skill-name", "args")
    skill_result = run_skill("skill-name", "args")
    print_results(skill_result)
    response = ask_user_question(...)
    result3 = extract_answer(response)
    phases[2]["complete"] = True
    update_header(phases)

    # PHASE 4
    print("\n[PHASE 4: Description]\n")
    response = ask_user_question(...)
    result4 = extract_answer(response)
    print_skill_execution("skill-name", "args")
    final_result = run_skill("skill-name", "args")
    phases[3]["complete"] = True
    update_header(phases)

    print("\n✅ Workflow complete!")
    return final_result
```

