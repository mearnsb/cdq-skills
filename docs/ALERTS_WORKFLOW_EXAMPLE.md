# Alerts Workflow — Complete Hybrid Implementation

This is a **complete working example** of the hybrid progressive disclosure pattern applied to create data quality alerts.

**Workflow Goal:** Create and configure alerts that notify users when DQ rules are violated

---

## Workflow Overview

```
═══════════════════════════════════════════════════════════════════════════════
☐ Rule Selection    ☐ Alert Config    ☐ Test Condition    ☐ Save Alert
═══════════════════════════════════════════════════════════════════════════════
```

**4 Phases:**

| Phase | Type | Interaction |
|-------|------|-------------|
| **1. Rule Selection** | Lightweight | Ask which rule, show available options |
| **2. Alert Config** | Interactive | Define threshold, recipients, channels |
| **3. Test Condition** | Validation | Run SQL to test alert condition works |
| **4. Save Alert** | Decision | Confirm and save to dataset |

---

## Phase 1: Rule Selection (Lightweight)

### Interaction Pattern

```
Header: ☐ Rule Selection    ☐ Alert Config    ☐ Test Condition    ☐ Save Alert

Step 1: Ask which dataset
Step 2: Run skill to list rules
Step 3: Ask user to pick rule
Step 4: Mark Phase 1 complete ✓
```

### Implementation

First, ask which dataset to work with:

```python
response1 = AskUserQuestion(questions=[{
    "question": "Which dataset should we create an alert for?",
    "header": "Rule Selection",
    "multiSelect": False,
    "options": [
        {"label": "AUTO_CDQ_ONB_samples.invoices", "description": "Invoices dataset"},
        {"label": "Other dataset", "description": "Specify a different dataset"}
    ]
}])

dataset = response1["Which dataset should we create..."]
```

**Display update:**
```
✓ Rule Selection    ☐ Alert Config    ☐ Test Condition    ☐ Save Alert

Dataset selected: AUTO_CDQ_ONB_samples.invoices ✓
```

Now run a skill to get available rules:

```python
# Run: cdq-get-rules --dataset AUTO_CDQ_ONB_samples.invoices
rules = run_skill("cdq-get-rules", args=f"--dataset '{dataset}'")

# Display rules
print_rules_table(rules)
```

**Displayed output:**
```
🔄 [RUNNING SKILL: cdq-get-rules --dataset "AUTO_CDQ_ONB_samples.invoices"]

Available Rules (10 total):
┌─────┬──────────────────────────────┬──────────┬──────────────┐
│ #   │ Rule Name                    │ Priority │ Violations   │
├─────┼──────────────────────────────┼──────────┼──────────────┤
│ 1   │ invoice_id_not_null          │ HIGH     │ 0            │
│ 2   │ issue_date_not_null          │ HIGH     │ 20           │
│ 3   │ invoice_id_uniqueness        │ HIGH     │ 0            │
│ 4   │ status_allowed_values        │ HIGH     │ 3            │
│ 5   │ amount_range_check           │ MEDIUM   │ 2            │
│ 6   │ customer_id_referential...   │ MEDIUM   │ 0            │
│ 7   │ issue_date_format_check      │ MEDIUM   │ 5            │
│ 8   │ amount_outlier_check         │ LOW      │ 15           │
│ 9   │ status_distribution_monitor  │ LOW      │ N/A          │
│ 10  │ customer_frequency_check     │ LOW      │ 8            │
└─────┴──────────────────────────────┴──────────┴──────────────┘
```

Now ask user to pick which rule:

```python
response2 = AskUserQuestion(questions=[{
    "question": "Which rule should trigger the alert?",
    "header": "Rule Selection",
    "multiSelect": False,
    "options": [
        {"label": "issue_date_not_null", "description": "HIGH - 20 current violations"},
        {"label": "status_allowed_values", "description": "HIGH - 3 current violations"},
        {"label": "amount_range_check", "description": "MEDIUM - 2 current violations"},
        {"label": "Other", "description": "Choose a different rule"}
    ]
}])

selected_rule = response2["Which rule should trigger..."]
```

**Mark Phase 1 complete:**
```
═══════════════════════════════════════════════════════════════════════════════
✓ Rule Selection    ☐ Alert Config    ☐ Test Condition    ☐ Save Alert
═══════════════════════════════════════════════════════════════════════════════

RULE SELECTED ✓
  Dataset: AUTO_CDQ_ONB_samples.invoices
  Rule: issue_date_not_null
  Current violations: 20
  Priority: HIGH
```

---

## Phase 2: Alert Configuration (Interactive)

### Interaction Pattern

```
Header: ✓ Rule Selection    ☐ Alert Config    ☐ Test Condition    ☐ Save Alert

Step 1: Ask alert threshold/condition
Step 2: Show example of what triggers alert
Step 3: Ask notification channels
Step 4: Ask who to notify
Step 5: Mark Phase 2 complete ✓
```

### Implementation

Ask for alert threshold:

```python
response3 = AskUserQuestion(questions=[{
    "question": "When should this alert trigger?",
    "header": "Alert Threshold",
    "multiSelect": False,
    "options": [
        {"label": "Any violations (fail_count > 0)", "description": "Alert on first failure (Recommended for HIGH priority)"},
        {"label": "Threshold: 1% of data fails", "description": "Alert if 1% or more records violate rule"},
        {"label": "Threshold: 5% of data fails", "description": "Alert if 5% or more records violate rule"},
        {"label": "Custom", "description": "Specify exact threshold"}
    ]
}])

threshold = response3["When should this alert trigger?"]
```

Show what this means in context:

```
Current data in dataset:
  • Total records: 1,000 (from last DQ job)
  • Current violations: 20
  • Current fail rate: 2%

Your threshold setting:
  • Trigger: If violations > 0
  • Current status: ⚠️ Would FAIL (has 20 violations)
  • Action: Alert would be ACTIVE now
```

Ask for notification channels:

```python
response4 = AskUserQuestion(questions=[{
    "question": "How should we notify about violations?",
    "header": "Notification Channels",
    "multiSelect": True,
    "options": [
        {"label": "Email", "description": "Send to notification recipients"},
        {"label": "Slack", "description": "Post to Slack channel"},
        {"label": "Dashboard", "description": "Show on CDQ dashboard only"},
        {"label": "Log file", "description": "Write to audit log"}
    ]
}])

channels = response4["How should we notify..."]
```

Ask who/where to notify:

```python
response5 = AskUserQuestion(questions=[{
    "question": "Who should receive notifications?",
    "header": "Recipients",
    "multiSelect": True,
    "options": [
        {"label": "Data Quality Team", "description": "team@company.com"},
        {"label": "Dataset Owner", "description": "owner@company.com"},
        {"label": "Custom", "description": "Specify email addresses or channels"}
    ]
}])

recipients = response5["Who should receive notifications?"]
```

**Mark Phase 2 complete:**

```
═══════════════════════════════════════════════════════════════════════════════
✓ Rule Selection    ✓ Alert Config    ☐ Test Condition    ☐ Save Alert
═══════════════════════════════════════════════════════════════════════════════

ALERT CONFIGURED ✓
  Rule: issue_date_not_null
  Trigger: Any violations (fail_count > 0)
  Current status: Would trigger ⚠️ (20 violations)

  Notify via: Email, Slack
  Recipients: Data Quality Team, Dataset Owner

  Alert summary:
  "When issue_date_not_null fails, email Data Quality Team and Dataset Owner"
```

---

## Phase 3: Test Condition (Validation Loop)

### Interaction Pattern

```
Header: ✓ Rule Selection    ✓ Alert Config    ☐ Test Condition    ☐ Save Alert

Step 1: Run SQL to test alert condition
Step 2: Display what records would trigger
Step 3: Show alert would fire (yes/no/maybe)
Step 4: Ask to proceed or modify
Step 5: Mark Phase 3 complete ✓
```

### Implementation

Test the alert condition by running the rule:

```python
# Download: The rule SQL from earlier
rule_sql = "SELECT * FROM samples.invoices WHERE issue_date IS NULL"

# Run: cdq-run-sql with COUNT to see how many violations
count_sql = f"SELECT COUNT(*) as total, SUM(CASE WHEN issue_date IS NULL THEN 1 ELSE 0 END) as violations FROM samples.invoices LIMIT 1"

results = run_skill("cdq-run-sql", args=f'--sql "{count_sql}"')
```

**Display test results:**

```
🔄 [RUNNING SKILL: cdq-run-sql with alert condition]

ALERT CONDITION TEST:
═══════════════════════════════════════════════════════════════════════════════

Rule SQL:
┌────────────────────────────────────────────────────────┐
│ SELECT * FROM samples.invoices WHERE issue_date IS NULL│
└────────────────────────────────────────────────────────┘

Current Data State:
┌──────────────────────────────────┐
│ Total records: 1,000             │
│ Records violating rule: 20       │
│ Fail rate: 2%                    │
└──────────────────────────────────┘

Alert Status:
  Threshold: Any violations (> 0)
  Current violations: 20
  Result: ⚠️ ALERT WOULD FIRE ✓

Alert message example:
  "issue_date_not_null rule failed with 20 violations (2% of data)"
```

Ask to proceed or modify:

```python
response6 = AskUserQuestion(questions=[{
    "question": "Alert condition tested successfully. Proceed?",
    "header": "Test Results",
    "multiSelect": False,
    "options": [
        {"label": "Yes, proceed to save", "description": "Alert condition is correct (Recommended)"},
        {"label": "Modify threshold", "description": "Go back and adjust alert trigger"},
        {"label": "Change recipients", "description": "Go back and modify who gets notified"},
        {"label": "Cancel", "description": "Don't create this alert"}
    ]
}])

proceed = response6["Alert condition tested..."]
```

**Mark Phase 3 complete:**

```
═══════════════════════════════════════════════════════════════════════════════
✓ Rule Selection    ✓ Alert Config    ✓ Test Condition    ☐ Save Alert
═══════════════════════════════════════════════════════════════════════════════

CONDITION VALIDATED ✓
  Test result: Alert would trigger with current data
  Status: Ready to save
```

---

## Phase 4: Save Alert (Decision)

### Interaction Pattern

```
Header: ✓ Rule Selection    ✓ Alert Config    ✓ Test Condition    ☐ Save Alert

Step 1: Show final alert configuration
Step 2: Ask final confirmation
Step 3: Run: cdq-save-alert
Step 4: Mark Phase 4 complete ✓
```

### Implementation

Show final configuration:

```
═══════════════════════════════════════════════════════════════════════════════
✓ Rule Selection    ✓ Alert Config    ✓ Test Condition    ☐ Save Alert
═══════════════════════════════════════════════════════════════════════════════

FINAL ALERT CONFIGURATION:
═══════════════════════════════════════════════════════════════════════════════

Dataset:         AUTO_CDQ_ONB_samples.invoices
Rule:            issue_date_not_null
Trigger:         Any violations (fail_count > 0)
Channels:        Email, Slack
Recipients:      Data Quality Team, Dataset Owner

Alert logic:
  IF (violations > 0) THEN
    SEND EMAIL to Data Quality Team, Dataset Owner
    POST TO Slack
    MESSAGE: "issue_date_not_null failed with {count} violations"
  END IF

Current status: Would trigger ⚠️ (20 violations exist)
```

Ask final confirmation:

```python
response7 = AskUserQuestion(questions=[{
    "question": "Ready to create this alert?",
    "header": "Confirm & Save",
    "multiSelect": False,
    "options": [
        {"label": "Yes, create alert", "description": "Save alert configuration (Recommended)"},
        {"label": "Review settings", "description": "Go back and modify configuration"},
        {"label": "Cancel", "description": "Don't create this alert"}
    ]
}])

save = response7["Ready to create..."]
```

Execute save:

```python
# Run: cdq-save-alert
alert_result = run_skill(
    "cdq-save-alert",
    args=f'--dataset "AUTO_CDQ_ONB_samples.invoices" --rule "issue_date_not_null" --threshold "any" --channels "email,slack" --recipients "dq-team,owner"'
)
```

**Mark Phase 4 complete and show results:**

```
═══════════════════════════════════════════════════════════════════════════════
✓ Rule Selection    ✓ Alert Config    ✓ Test Condition    ✓ Save Alert
═══════════════════════════════════════════════════════════════════════════════

🎉 ALERT CREATED SUCCESSFULLY

Alert Details:
  • Alert ID: alert_20250409_001
  • Dataset: AUTO_CDQ_ONB_samples.invoices
  • Rule: issue_date_not_null
  • Status: ✓ ACTIVE
  • Created: 2025-04-09 14:32:15 UTC

  Next steps:
  → Alert will check on next DQ job run
  → Recipients will receive notifications
  → Monitor alert activity on dashboard

Next actions:
  1. Create another alert
  2. View alert activity
  3. Exit
```

---

## Complete Workflow Code Template

```python
def run_alerts_workflow():
    """Complete Alerts workflow using hybrid pattern"""

    # Print initial header
    print_header([
        ("Rule Selection", False),
        ("Alert Config", False),
        ("Test Condition", False),
        ("Save Alert", False)
    ])

    # PHASE 1: Rule Selection
    print("\n[PHASE 1: Rule Selection]\n")

    # Ask dataset
    r1 = ask_user_question("Which dataset?", [
        ("AUTO_CDQ_ONB_samples.invoices", "Invoices"),
        ("Other", "Custom dataset")
    ])
    dataset = r1

    # Get rules (skill execution)
    print("🔄 [RUNNING SKILL: cdq-get-rules]")
    rules = run_skill("cdq-get-rules", f"--dataset '{dataset}'")
    print_rules_table(rules)

    # Ask which rule
    r2 = ask_user_question("Which rule?", [
        (rule["name"], f"{rule['priority']} - {rule['violations']} violations")
        for rule in rules
    ])
    selected_rule = r2

    # Mark complete
    mark_section_complete("Rule Selection")
    print_header([
        ("Rule Selection", True),
        ("Alert Config", False),
        ("Test Condition", False),
        ("Save Alert", False)
    ])

    # PHASE 2: Alert Configuration
    print("\n[PHASE 2: Alert Configuration]\n")

    # Ask threshold
    r3 = ask_user_question("When trigger?", [
        ("any", "Any violations"),
        ("1pct", "1% threshold"),
        ("5pct", "5% threshold")
    ])
    threshold = r3

    # Show impact
    print_threshold_impact(dataset, selected_rule, threshold)

    # Ask channels
    r4 = ask_user_multi_select("Notification channels?", [
        ("email", "Email"),
        ("slack", "Slack"),
        ("dashboard", "Dashboard")
    ])
    channels = r4

    # Ask recipients
    r5 = ask_user_multi_select("Recipients?", [
        ("dq-team", "DQ Team"),
        ("owner", "Owner"),
        ("custom", "Custom")
    ])
    recipients = r5

    # Mark complete
    mark_section_complete("Alert Config")
    print_header([
        ("Rule Selection", True),
        ("Alert Config", True),
        ("Test Condition", False),
        ("Save Alert", False)
    ])

    # PHASE 3: Test Condition
    print("\n[PHASE 3: Test Condition]\n")

    # Run test (skill execution)
    print("🔄 [RUNNING SKILL: cdq-run-sql to test condition]")
    test_result = run_skill("cdq-run-sql", f"--sql '{get_rule_sql(selected_rule)}'")
    print_test_results(test_result, threshold)

    # Ask proceed
    r6 = ask_user_question("Proceed?", [
        ("yes", "Yes, save alert"),
        ("modify", "Modify settings"),
        ("cancel", "Cancel")
    ])

    if r6 == "cancel":
        return "Cancelled by user"
    elif r6 == "modify":
        # Loop back to Phase 2
        return run_alerts_workflow()

    # Mark complete
    mark_section_complete("Test Condition")
    print_header([
        ("Rule Selection", True),
        ("Alert Config", True),
        ("Test Condition", True),
        ("Save Alert", False)
    ])

    # PHASE 4: Save Alert
    print("\n[PHASE 4: Save Alert]\n")

    # Show final config
    print_final_config(dataset, selected_rule, threshold, channels, recipients)

    # Ask final confirmation
    r7 = ask_user_question("Create alert?", [
        ("yes", "Yes, create"),
        ("no", "No, cancel")
    ])

    if r7 == "no":
        return "Cancelled by user"

    # Save (skill execution)
    print("🔄 [RUNNING SKILL: cdq-save-alert]")
    result = run_skill("cdq-save-alert",
        f"--dataset '{dataset}' --rule '{selected_rule}' " +
        f"--threshold '{threshold}' --channels '{channels}' " +
        f"--recipients '{recipients}'"
    )

    # Mark complete
    mark_section_complete("Save Alert")
    print_header([
        ("Rule Selection", True),
        ("Alert Config", True),
        ("Test Condition", True),
        ("Save Alert", True)
    ])

    print(f"\n✅ Alert created successfully!")
    print(f"Alert ID: {result['alert_id']}")

    return result
```

---

## Key Features in This Implementation

✅ **4-phase workflow** with multi-section headers
✅ **Phase 1:** Lightweight dataset/rule selection
✅ **Phase 2:** Interactive configuration with impact preview
✅ **Phase 3:** Validation loop with SQL testing
✅ **Phase 4:** Final confirmation and save
✅ **Skill integration** at strategic points
✅ **Raw output display** (SQL, test results, configuration)
✅ **User feedback loops** (modify/retry options)
✅ **Error handling** (cancel, go back)

---

## Related Workflows

- `docs/DISCOVERY_WORKFLOW_EXAMPLE.md` - Table discovery pattern
- `docs/ONBOARDING_WORKFLOW_EXAMPLE.md` - Dataset onboarding pattern
- `docs/RULES_WORKFLOW_EXAMPLE.md` - Rule creation pattern
- `docs/HYBRID_PROGRESSIVE_DISCLOSURE_PATTERN.md` - General pattern guide

