# Gemini CLI Setup & Usage Guide

Complete guide to using Gemini CLI with the CDQ Skills project, including fixing the "Exit Code 41" environment error.

## Quick Start

### 1. Verify Your Setup
```bash
# Check that your API key is configured
cat ~/.openclaw/.env | grep GEMINI_API_KEY

# Expected output:
# GEMINI_API_KEY=sk-... (should show a value, not empty)
```

### 2. Load Environment Variables
```bash
# Option A: Load for current shell session ONLY
set -a
source ~/.openclaw/.env
set +a

# Option B: Load and verify it worked
source ~/.openclaw/.env
echo "API Key loaded: $GEMINI_API_KEY" | head -c 30

# Option C: Add to ~/.zshrc for persistence (RECOMMENDED)
echo 'set -a; [ -f ~/.openclaw/.env ] && source ~/.openclaw/.env; set +a' >> ~/.zshrc
source ~/.zshrc
```

### 3. Test Gemini CLI Works
```bash
# Minimal test
gemini -p "Say hello" -m gemini-2.5-flash

# Expected: Gemini responds with a greeting (no exit code 41)
```

---

## Common Usage Examples

### Example 1: Basic Code Review
```bash
# Review a specific file
gemini -p "Review this code for security issues: $(cat src/main.py)" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Example 2: Big Context Analysis (use for >200k tokens)
```bash
# Analyze large codebase
gemini -p "Analyze the architecture of this project and summarize patterns" \
  -m gemini-2.5-flash \
  --approval-mode auto_edit
```

### Example 3: Research Task with Tool Use
```bash
# Extended research (allows MCP tools, code execution)
gemini -p "Research how elite developers use open-weight models" \
  -m gemini-2.5-flash \
  --approval-mode auto_edit
```

### Example 4: Interactive Mode
```bash
# Start interactive session (no -p flag)
gemini -m gemini-2.5-flash

# Then type prompts and interact - press Ctrl+C to exit
```

---

## Fixing "Exit Code 41" Error

**Problem**: `When using Gemini API, you must specify the GEMINI_API_KEY environment variable`

### Root Cause
The environment variable isn't being exported to the gemini subprocess. Simply running `source ~/.openclaw/.env` isn't enough.

### Solutions (in order of preference)

#### Solution 1: Add to Shell Config (PERMANENT)
```bash
# Add this line to ~/.zshrc (or ~/.bashrc for Bash)
set -a; [ -f ~/.openclaw/.env ] && source ~/.openclaw/.env; set +a

# Then reload:
source ~/.zshrc

# Verify:
echo $GEMINI_API_KEY  # Should show your key
```

#### Solution 2: Load Before Running Gemini (TEMPORARY)
```bash
# Run this before each gemini command
set -a && source ~/.openclaw/.env && set +a

# Or create an alias:
alias gemini-safe='set -a && source ~/.openclaw/.env && set +a && gemini'

# Then use normally:
gemini-safe -p "your prompt"
```

#### Solution 3: Use the Wrapper Script (RECOMMENDED FOR THIS PROJECT)
See "Wrapper Script Setup" section below.

---

## Wrapper Script Setup

For the most reliable experience, use this wrapper script that automatically handles environment loading.

### Step 1: Create the Wrapper Script
```bash
mkdir -p ~/.openclaw/bin

cat > ~/.openclaw/bin/gemini-wrapper.sh << 'EOF'
#!/bin/bash
set -e

# Self-healing environment loading
set -a
if [ -f ~/.openclaw/.env ]; then
    source ~/.openclaw/.env
else
    echo "ERROR: ~/.openclaw/.env not found" >&2
    echo "Create it with: echo 'GEMINI_API_KEY=sk-...' > ~/.openclaw/.env" >&2
    exit 1
fi
set +a

# Validate required variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: GEMINI_API_KEY not set in ~/.openclaw/.env" >&2
    echo ""
    echo "Fix this:"
    echo "  1. Edit ~/.openclaw/.env"
    echo "  2. Add line: GEMINI_API_KEY=sk-yourkeyhere"
    echo "  3. Save and retry"
    exit 1
fi

# Execute gemini with all args passed through
exec /opt/homebrew/bin/gemini "$@"
EOF

chmod +x ~/.openclaw/bin/gemini-wrapper.sh
```

### Step 2: Create Alias
```bash
# Add to ~/.zshrc (or ~/.bashrc)
alias gemini='~/.openclaw/bin/gemini-wrapper.sh'

# Reload:
source ~/.zshrc
```

### Step 3: Test It Works
```bash
# This should work even if GEMINI_API_KEY wasn't exported before
gemini -p "Say hello" -m gemini-2.5-flash

# Expected: Should run successfully
# If it fails: see the diagnostic error message
```

---

## Approval Modes Explained

Use the right approval mode for your task:

| Mode | Use When | Example |
|------|----------|---------|
| `default` | Want to review each tool call individually | Security-critical operations |
| `auto_edit` | OK auto-approving file edits but reviewing other tools | Small refactors |
| `yolo` | Trust Gemini completely, auto-approve everything | Safe research/analysis tasks |
| `plan` | Read-only mode, no tool execution | Planning phase only |

```bash
# Examples:
gemini -p "..." --approval-mode default       # Prompt for each tool
gemini -p "..." --approval-mode auto_edit     # Auto-approve edits only
gemini -p "..." --approval-mode yolo          # Auto-approve everything
gemini -p "..." --approval-mode plan          # Read-only planning
```

---

## Model Selection

### Recommended Models
```bash
# Best for general tasks (latest)
gemini -m gemini-2.5-flash "your prompt"

# For reasoning/complex analysis
gemini -m gemini-2.0-pro-exp "your prompt"

# For extended context (up to 1M tokens)
gemini -m gemini-2.0-flash-exp "your prompt"
```

---

## Troubleshooting

### Issue: "Exit code 41" appears
**Solution**: Run the diagnostic wrapper script
```bash
~/.openclaw/bin/gemini-wrapper.sh -p "test"

# Should show clear error message with steps to fix
```

### Issue: "API quota exceeded"
**Solution**: Wait and retry. Check your usage:
```bash
# No built-in command, check Google Cloud Console
# https://console.cloud.google.com/apis/api/generativeai.googleapis.com/quotas
```

### Issue: Gemini command not found
**Solution**: Install Gemini CLI
```bash
# Using Homebrew
brew install gemini-cli

# Or download from: https://github.com/google-gemini/gemini-cli
```

### Issue: Wrong API key format
**Solution**: Verify your key
```bash
# Should start with "sk-" and be long (100+ chars)
echo $GEMINI_API_KEY | head -c 50

# Get a new key from:
# https://aistudio.google.com/apikey
```

---

## Integration with Claude Code

When using Gemini CLI skill in Claude Code:

```bash
# Claude Code will run:
source ~/.openclaw/.env && gemini -p "..." -m gemini-2.5-flash

# But this can fail due to environment leak
# Better: Use the wrapper
~/.openclaw/bin/gemini-wrapper.sh -p "..." -m gemini-2.5-flash
```

---

## Best Practices

1. **Always use `set -a` when loading `.env`**
   ```bash
   set -a && source ~/.openclaw/.env && set +a
   ```

2. **Test before using in automation**
   ```bash
   # Manual test first
   gemini -p "test" -m gemini-2.5-flash
   ```

3. **Use the wrapper script for reliability**
   ```bash
   gemini-safe -p "..." -m gemini-2.5-flash
   ```

4. **Add appropriate approval mode**
   ```bash
   # NOT this (risky by default)
   gemini -p "create a script"

   # DO this (explicit mode)
   gemini -p "create a script" --approval-mode yolo
   ```

5. **Monitor usage**
   - Check Google Cloud Console for API usage
   - Set up billing alerts
   - Use `--approval-mode plan` for planning-only runs

---

## Related Documentation

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [CDQ Skills Setup](./SETUP.md)
- [CDQ Skills Examples](./EXAMPLE_PROMPTS.md)
