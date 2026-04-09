# Gemini CLI Examples - Real-World Usage

Concrete, copy-paste-ready examples for using Gemini CLI with the CDQ Skills project.

---

## Setup Examples

### Example: First-Time Setup
```bash
# Step 1: Create ~/.openclaw/.env with your API key
# (Get key from https://aistudio.google.com/apikey)
echo "GEMINI_API_KEY=sk-$(your-api-key-here)" > ~/.openclaw/.env

# Step 2: Make wrapper executable
chmod +x ~/.claude/bin/gemini-wrapper.sh

# Step 3: Add to ~/.zshrc
echo 'alias gemini-safe=~/.claude/bin/gemini-wrapper.sh' >> ~/.zshrc
source ~/.zshrc

# Step 4: Test it works
gemini-safe --check

# Expected output:
# 🔍 Checking Gemini Configuration...
# ✅ .env file found
# ✅ Gemini binary found
# ✅ GEMINI_API_KEY found
# ✅ All checks passed! Ready to use.
```

### Example: Load Environment for Current Session
```bash
# Option 1: Using the wrapper (RECOMMENDED)
~/.claude/bin/gemini-wrapper.sh -p "Say hello" -m gemini-2.5-flash

# Option 2: Manual load for bash scripts
set -a
source ~/.openclaw/.env
set +a
gemini -p "Say hello" -m gemini-2.5-flash

# Option 3: One-liner
set -a && source ~/.openclaw/.env && set +a && gemini -p "Say hello" -m gemini-2.5-flash
```

---

## Code Review Examples

### Example 1: Review a Python File
```bash
# Simple file review
~/.claude/bin/gemini-wrapper.sh \
  -p "Review this Python code for security issues: $(cat src/auth.py)" \
  -m gemini-2.5-flash \
  --approval-mode yolo

# Expected: Detailed security review of the code
```

### Example 2: Review Specific Function
```bash
# Extract function and review
~/.claude/bin/gemini-wrapper.sh \
  -p "This is a login function. Find bugs:

$(sed -n '/def login/,/^def /p' app.py | head -n -1)" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Example 3: Review from File Path
```bash
# Review arbitrary files
for file in src/*.py; do
  echo "=== Reviewing $file ==="
  ~/.claude/bin/gemini-wrapper.sh \
    -p "Security review: $(cat "$file")" \
    -m gemini-2.5-flash \
    --approval-mode yolo
done
```

---

## Analysis Examples

### Example 1: Analyze Project Architecture
```bash
# Get overview of project structure
PROJECT_FILES=$(find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.json" \) | head -20)

~/.claude/bin/gemini-wrapper.sh \
  -p "Analyze this project structure and summarize the architecture:

$PROJECT_FILES

Main files: $(cat README.md | head -50)" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Example 2: Code Quality Analysis
```bash
# Analyze code patterns and quality
~/.claude/bin/gemini-wrapper.sh \
  -p "Analyze code quality issues in these files:

1. $(cat src/main.py | wc -l) lines - main.py
2. $(cat src/utils.py | wc -l) lines - utils.py
3. $(cat src/config.py | wc -l) lines - config.py

Find patterns, duplications, and improvements" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Example 3: Research (Using MCP Tools)
```bash
# Extended research that can use tools
~/.claude/bin/gemini-wrapper.sh \
  -p "Research how elite developers use open-weight models like Qwen, DeepSeek, and Mistral.
What are the key advantages? Best practices? When to use them?" \
  -m gemini-2.5-flash \
  --approval-mode auto_edit
```

---

## Development with Gemini

### Example 1: Generate Boilerplate Code
```bash
~/.claude/bin/gemini-wrapper.sh \
  -p "Generate a Python Flask API endpoint for user authentication with:
  - JWT tokens
  - Password hashing with bcrypt
  - Input validation
  - Error handling

Include tests." \
  -m gemini-2.5-flash \
  --approval-mode auto_edit
```

### Example 2: Help with Debugging
```bash
# Paste error message and request debugging help
ERROR_LOG=$(cat debug.log | tail -50)

~/.claude/bin/gemini-wrapper.sh \
  -p "Debug this error. What's the root cause?

Error:
$ERROR_LOG

Context: This happens when running data validation on large files" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Example 3: Explain Code
```bash
# Paste complex code and get explanation
~/.claude/bin/gemini-wrapper.sh \
  -p "Explain what this code does step-by-step:

$(cat src/complex_algorithm.py)" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

---

## CDQ-Specific Examples

### Example 1: Plan Data Quality Rules
```bash
# Get suggestions for DQ rules
~/.claude/bin/gemini-wrapper.sh \
  -p "Suggest data quality rules for a customer table with these columns:
  - customer_id (integer)
  - name (string, max 255)
  - email (string, must be unique)
  - created_date (timestamp)
  - is_active (boolean)

Focus on: nullness, uniqueness, format validation, business logic checks" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Example 2: Review DQ Rule SQL
```bash
# Validate DQ rule before saving
RULE_SQL="SELECT COUNT(*) FROM customers WHERE email IS NULL OR email NOT LIKE '%@%.%'"

~/.claude/bin/gemini-wrapper.sh \
  -p "Review this data quality rule SQL:

$RULE_SQL

Is it correct? Will it catch real issues? Any edge cases?" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Example 3: Analyze DQ Results
```bash
# Analyze DQ job results
DQ_RESULTS="Rule: null_emails - Found: 42 records
Rule: invalid_phone - Found: 128 records
Rule: duplicate_names - Found: 0 records
Overall Score: 94.2%"

~/.claude/bin/gemini-wrapper.sh \
  -p "Interpret these data quality results:

$DQ_RESULTS

What issues need immediate attention? What's the priority?" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

---

## Integration Examples

### Example 1: Batch Analysis Script
```bash
#!/bin/bash
# analyze-files.sh - Analyze multiple files

set -a
source ~/.openclaw/.env
set +a

for file in src/*.py; do
    echo "Analyzing: $file"
    ~/.claude/bin/gemini-wrapper.sh \
        -p "Quick security audit of $(basename $file):

$(cat "$file")" \
        -m gemini-2.5-flash \
        --approval-mode yolo > "audit-$(basename $file).txt"
done

echo "✅ Analysis complete. See audit-*.txt files"
```

### Example 2: Git Pre-Commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit - Check code before committing

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

for file in $STAGED_FILES; do
    if [[ $file == *.py ]] || [[ $file == *.js ]]; then
        echo "Checking: $file"

        set -a
        source ~/.openclaw/.env
        set +a

        ~/.claude/bin/gemini-wrapper.sh \
            -p "Quick code review of staged changes in $file. Any blocking issues?

$(git diff --cached "$file")" \
            -m gemini-2.5-flash \
            --approval-mode yolo
    fi
done
```

### Example 3: Cron Job for Regular Analysis
```bash
# Add to crontab: 0 6 * * * /Users/brian/github/cdq-skills/scripts/daily-analysis.sh

#!/bin/bash
# daily-analysis.sh - Run daily code analysis

source ~/.openclaw/.env

# Analyze recent changes
CHANGES=$(git log --oneline -10)

~/.claude/bin/gemini-wrapper.sh \
    -p "Summarize the patterns in these recent code changes:

$CHANGES

Any architectural concerns?" \
    -m gemini-2.5-flash \
    --approval-mode yolo | \
    mail -s "Daily Code Analysis" brian@example.com
```

---

## Interactive Mode Examples

### Example 1: Start Interactive Session
```bash
# Start interactive conversation
set -a && source ~/.openclaw/.env && set +a
gemini -m gemini-2.5-flash

# Then type prompts and interact
# Type your prompts, Gemini responds
# Press Ctrl+C to exit
```

### Example 2: Interactive with Initial Prompt
```bash
# Start interactive but with a starting question
set -a && source ~/.openclaw/.env && set +a
gemini -i "Help me debug a Python error" -m gemini-2.5-flash

# Gemini answers the initial prompt
# Then you can continue the conversation
```

---

## Approval Mode Examples

### Example 1: Safe Planning Mode (Read-Only)
```bash
# Plan without executing tools
~/.claude/bin/gemini-wrapper.sh \
    -p "Plan how to refactor this codebase. What steps would you take?" \
    -m gemini-2.5-flash \
    --approval-mode plan  # read-only, no tool execution

# Gemini plans but can't execute tools
```

### Example 2: Auto-Edit Mode (Safe for Edits)
```bash
# Auto-approve file edits, prompt for other tools
~/.claude/bin/gemini-wrapper.sh \
    -p "Refactor this code to be more efficient: $(cat src/slow.py)" \
    -m gemini-2.5-flash \
    --approval-mode auto_edit

# Gemini auto-approves code edits
# Prompts for other tool calls (bash, etc)
```

### Example 3: Yolo Mode (Trust Gemini)
```bash
# Auto-approve everything
~/.claude/bin/gemini-wrapper.sh \
    -p "Create a complete REST API with tests" \
    -m gemini-2.5-flash \
    --approval-mode yolo  # auto-approve all tools

# WARNING: Only use for tasks you fully trust!
```

---

## Troubleshooting Examples

### Example 1: Check Configuration
```bash
# Diagnose environment issues
~/.claude/bin/gemini-wrapper.sh --check

# Output shows what's configured and what's missing
```

### Example 2: Debug Failed Command
```bash
# Run with debug output
~/.claude/bin/gemini-wrapper.sh \
    --debug \
    -p "test" \
    -m gemini-2.5-flash

# Shows environment loading and command details
```

### Example 3: Verify API Key
```bash
# Check if API key is properly loaded
echo "API Key preview: ${GEMINI_API_KEY:0:20}..."

# Should show: API Key preview: sk-...
# If empty, key wasn't loaded
```

---

## Real-World Workflows

### Workflow 1: Code Review Before Commit
```bash
# 1. Get files to commit
git diff --cached --name-only

# 2. Review with Gemini
for file in $(git diff --cached --name-only); do
    echo "=== Reviewing $file ==="
    ~/.claude/bin/gemini-wrapper.sh \
        -p "Review these changes for issues:

$(git diff --cached $file)" \
        -m gemini-2.5-flash \
        --approval-mode yolo
done

# 3. If issues found, fix and retry
# 4. Commit if approved
```

### Workflow 2: Daily Development Session
```bash
# 1. Load environment once
set -a && source ~/.openclaw/.env && set +a

# 2. Run multiple analyses
gemini -i "What should I focus on today?" -m gemini-2.5-flash

# Start interactive session, have conversation
# Gemini can help with:
# - Code reviews
# - Debugging
# - Architecture decisions
# - Testing strategies
```

### Workflow 3: Bug Investigation
```bash
# 1. Gather error details
ERROR_LOG=$(tail -100 error.log)
STACK_TRACE=$(cat stack-trace.txt)
RECENT_CHANGES=$(git diff HEAD~5)

# 2. Ask Gemini to investigate
~/.claude/bin/gemini-wrapper.sh \
    -p "Debug this issue:

Error Log:
$ERROR_LOG

Stack Trace:
$STACK_TRACE

Recent Changes:
$RECENT_CHANGES" \
    -m gemini-2.5-flash \
    --approval-mode yolo

# 3. Got suggestion? Test it
# 4. Document solution
```

---

## Tips & Tricks

### Tip 1: Save API Key from Command Line
```bash
# Copy from Google AI Studio, then:
read GEMINI_API_KEY
echo "GEMINI_API_KEY=$GEMINI_API_KEY" >> ~/.openclaw/.env
```

### Tip 2: Create Custom Aliases
```bash
# Add to ~/.zshrc
alias gem='~/.claude/bin/gemini-wrapper.sh'
alias gem-plan='~/.claude/bin/gemini-wrapper.sh --approval-mode plan'
alias gem-edit='~/.claude/bin/gemini-wrapper.sh --approval-mode auto_edit'
alias gem-yolo='~/.claude/bin/gemini-wrapper.sh --approval-mode yolo'

# Usage:
gem -p "hello" -m gemini-2.5-flash
gem-plan -p "plan this"
```

### Tip 3: Pipe File Content
```bash
# Instead of cat inside -p flag
cat huge-file.py | ~/.claude/bin/gemini-wrapper.sh \
    -p "Review: $(cat)" \
    -m gemini-2.5-flash

# Or use xargs
find . -name "*.py" | xargs -I {} bash -c \
    '~/.claude/bin/gemini-wrapper.sh -p "Review: $(cat {})" ...'
```

### Tip 4: Combine with Other Tools
```bash
# Use with jq for API responses
curl -s https://api.example.com/data | jq . | \
    ~/.claude/bin/gemini-wrapper.sh \
    -p "Analyze this API response: $(cat)" \
    -m gemini-2.5-flash

# Use with grep for specific errors
grep ERROR debug.log | \
    ~/.claude/bin/gemini-wrapper.sh \
    -p "What are these errors: $(cat)" \
    -m gemini-2.5-flash
```

---

## See Also

- [Gemini Setup Guide](./GEMINI_SETUP_GUIDE.md) - Detailed setup instructions
- [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md) - CDQ-specific examples
- [Gemini API Docs](https://ai.google.dev/docs)
