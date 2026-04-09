# Gemini CLI - Quick Reference Card

## TL;DR - 30 Second Setup

**Assuming `gsearch` alias is configured** (see [Alias Configuration](#alias-configuration) below):

```bash
# 1. Verify API key is loaded
cat ~/.openclaw/.env | grep GEMINI_API_KEY

# 2. Use gsearch (minimal — everything defaults)
gsearch -p "Your prompt here"

# 3. Override defaults if needed
gsearch -p "Your prompt" --approval-mode auto_edit    # See tool calls
gsearch -p "Your prompt" -m gemini-2.5-flash          # Use faster model
```

**Without alias?** Use the full path:
```bash
~/.claude/bin/gemini-search -p "Your prompt here"
```

---

## Web-Search & Rapid Queries

Use `gsearch` for instant web research with built-in defaults (flash-lite + yolo):

```bash
# Minimal — just the prompt
gsearch -p "latest news on open source LLMs April 2026"

# Multi-line query for structured results
gsearch -p "Search the web for:
1. Latest open source LLM releases
2. Performance benchmarks March-April 2026
3. Industry adoption trends"

# See tool calls being executed
gsearch -p "Search for..." --approval-mode auto_edit

# Use stronger model for complex analysis
gsearch -p "Analyze trends and implications..." -m gemini-2.5-flash
```

---

## Most Common Commands

### Simple Prompt (minimal, uses defaults)
```bash
gsearch -p "Say hello"
```

### With Specific Model
```bash
gsearch -p "Say hello" -m gemini-2.5-flash
```

### Code Review
```bash
gsearch -p "Review this for security: $(cat app.py)"
```

### Analyze with Visibility
```bash
gsearch -p "Analyze: $(cat error.log)" --approval-mode auto_edit
```

### Interactive Mode (terminal only)
```bash
set -a && source ~/.openclaw/.env && set +a
gemini -m gemini-2.5-flash --approval-mode default
# Then type prompts...
```

### Using Full Path (without alias)
```bash
~/.claude/bin/gemini-search -p "Your prompt here"
```

---

## Approval Modes

| Mode | Auto-Approve | Use When |
|------|--------------|----------|
| `default` | None | Want to review each tool |
| `auto_edit` | File edits | Small, safe changes |
| `yolo` | Everything | Trust Gemini completely |
| `plan` | Nothing (read-only) | Planning only |

```bash
# Examples:
~/.claude/bin/gemini-wrapper.sh -p "test" --approval-mode default     # Prompt for approval
~/.claude/bin/gemini-wrapper.sh -p "test" --approval-mode auto_edit   # Auto-approve edits
~/.claude/bin/gemini-wrapper.sh -p "test" --approval-mode yolo        # Auto-approve all
~/.claude/bin/gemini-wrapper.sh -p "test" --approval-mode plan        # Read-only
```

---

## Models

**Default: `gemini-2.5-flash-lite`** (automatically used if -m not specified)

```bash
# Eligible models for testing (smallest to largest):
-m gemini-2.5-flash-lite      # Default - lightweight, fast, good for most tasks
-m gemini-2.5-flash           # Latest flagship model
-m gemini-2.0-flash-exp       # Extended context (up to 1M tokens)
-m gemini-1.5-pro             # For complex reasoning

# Override default:
export GEMINI_DEFAULT_MODEL=gemini-2.5-flash
~/.claude/bin/gemini-wrapper.sh -p "your prompt"
```

---

## File Input Tricks

### Pipe content into prompt
```bash
gsearch -p "Review: $(cat app.py)"
```

### Review recent git changes
```bash
gsearch -p "Review: $(git diff HEAD)" -m gemini-2.5-flash
```

### Analyze error logs
```bash
gsearch -p "Debug this: $(tail -50 error.log)"
```

### Review multiple files
```bash
gsearch -p "Review for bugs:

app.py:
$(cat app.py)

utils.py:
$(cat utils.py)"
```

---

## Troubleshooting

### "gsearch: command not found"
```bash
# Make sure alias is in ~/.zshrc (see setup below)
source ~/.zshrc

# Or use full path instead:
~/.claude/bin/gemini-search -p "Your prompt"
```

### "Exit code 41: GEMINI_API_KEY not found"
```bash
# Run diagnostic
~/.claude/bin/gemini-search -p "test"

# If fails, add to ~/.zshrc:
echo 'set -a; [ -f ~/.openclaw/.env ] && source ~/.openclaw/.env; set +a' >> ~/.zshrc
source ~/.zshrc
```

### "gemini: command not found"
```bash
# Install Gemini CLI
brew install gemini-cli
```

---

## Alias Configuration

Add to `~/.zshrc` (recommended):

```bash
# Primary alias for web search + rapid queries (uses flash-lite + yolo defaults)
alias gsearch='~/.claude/bin/gemini-search'

# Optional: additional convenience aliases
alias gsearch-edit='~/.claude/bin/gemini-search --approval-mode auto_edit'
alias gsearch-flash='~/.claude/bin/gemini-search -m gemini-2.5-flash'
alias gsearch-flash-edit='~/.claude/bin/gemini-search -m gemini-2.5-flash --approval-mode auto_edit'
```

Then reload:
```bash
source ~/.zshrc
```

### Usage Examples
```bash
# Basic (defaults: flash-lite + yolo)
gsearch -p "Search for latest LLM trends"

# See tool calls
gsearch-edit -p "Research cloud trends"

# Stronger model
gsearch-flash -p "Complex analysis needed"

# Stronger model + visibility
gsearch-flash-edit -p "Detailed code review"
```

---

## CDQ + Gemini Workflows

### Plan DQ Rules (minimal)
```bash
gsearch -p "Suggest DQ rules for table with: id, email, name, created_at"
```

### Understand DQ Results
```bash
gsearch -p "Analyze these DQ findings: null_emails=42, invalid_format=128"
```

### Review Data Quality Rule SQL
```bash
gsearch -p "Review this DQ rule: SELECT * FROM {dataset} WHERE email IS NULL"
```

### Complex Analysis (stronger model)
```bash
gsearch -p "Design comprehensive DQ strategy for..." -m gemini-2.5-flash
```

---

## Full Documentation

- [Gemini Setup Guide](./GEMINI_SETUP_GUIDE.md) - Complete setup, approval modes, troubleshooting
- [Gemini Examples](./GEMINI_EXAMPLES.md) - 30+ real-world examples
- [CDQ Skills README](./README.md) - CDQ concepts and workflows
- [Example Prompts](./EXAMPLE_PROMPTS.md) - Multi-step CDQ workflows

---

## Key Files & Configuration

| File | Purpose |
|------|---------|
| `~/.claude/bin/gemini-search` | Main script (auto-loads API key, sets defaults) |
| `~/.openclaw/.env` | API credentials (GEMINI_API_KEY) |
| `~/.zshrc` | Shell config (for `gsearch` alias) |
| `.claude/skills/gemini/SKILL.md` | Claude Code skill documentation |

---

## Useful Links

- [Gemini API Docs](https://ai.google.dev/docs)
- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Get API Key](https://aistudio.google.com/apikey)
- [CDQ Skills GitHub](https://github.com/collibra/cdq-skills)
