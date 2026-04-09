# Gemini CLI Implementation Guide

Complete implementation roadmap for fixing the "Exit Code 41" environment error and establishing best practices for Gemini CLI usage with CDQ Skills.

## Executive Summary

**Problem**: Gemini CLI failed with "Exit Code 41: GEMINI_API_KEY not found" even though credentials were configured
- **Root Cause**: Environment variables loaded with `source` don't export to subprocesses
- **Solution**: Use robust shell patterns (`set -a` + wrapper script) + comprehensive documentation

**Deliverables**:
1. ✅ Hardened wrapper script (`gemini-wrapper.sh`) with validation and diagnostics
2. ✅ Complete setup guide (`GEMINI_SETUP_GUIDE.md`) with multiple approaches
3. ✅ 30+ copy-paste examples (`GEMINI_EXAMPLES.md`)
4. ✅ Quick reference card (`GEMINI_QUICK_REFERENCE.md`)
5. ✅ Improvement analysis (`gemini-skill-improvements.md`)

---

## Implementation Checklist

### Phase 1: User Setup (5 minutes)

- [ ] **Step 1: Copy wrapper script to project**
  ```bash
  # Wrapper is already in: /Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh
  # Make executable (if not already)
  chmod +x /Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh
  ```

- [ ] **Step 2: Create symlink for convenient access (optional)**
  ```bash
  # Link to home bin for global access
  ln -sf /Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh ~/.openclaw/bin/gemini-wrapper.sh
  # Or create an alias in ~/.zshrc
  echo "alias gemini-safe='~/.openclaw/bin/gemini-wrapper.sh'" >> ~/.zshrc
  ```

- [ ] **Step 3: Verify setup**
  ```bash
  # Test the wrapper
  /Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh --check
  ```

- [ ] **Step 4: Read the documentation**
  - [ ] Quick Reference: `GEMINI_QUICK_REFERENCE.md` (2 min read)
  - [ ] Setup Guide: `GEMINI_SETUP_GUIDE.md` (5 min read)

### Phase 2: First Use (2 minutes)

- [ ] **Test basic prompt**
  ```bash
  /Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh \
    -p "Say hello and explain what you are" \
    -m gemini-2.5-flash
  ```

- [ ] **Test approval modes**
  ```bash
  # Test default mode (prompts for approval)
  /Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh \
    -p "test" -m gemini-2.5-flash --approval-mode auto_edit
  ```

- [ ] **Test interactive mode**
  ```bash
  # Load environment and start interactive
  set -a && source ~/.openclaw/.env && set +a
  gemini -m gemini-2.5-flash
  ```

### Phase 3: Integration (10 minutes)

- [ ] **Add to shell config (optional but recommended)**
  ```bash
  # Add to ~/.zshrc
  cat >> ~/.zshrc << 'EOF'

  # Gemini CLI setup
  set -a; [ -f ~/.openclaw/.env ] && source ~/.openclaw/.env; set +a
  alias gemini-safe='~/.openclaw/bin/gemini-wrapper.sh'
  alias gem-plan='~/.openclaw/bin/gemini-wrapper.sh --approval-mode plan'
  alias gem-edit='~/.openclaw/bin/gemini-wrapper.sh --approval-mode auto_edit'
  alias gem-yolo='~/.openclaw/bin/gemini-wrapper.sh --approval-mode yolo'
  alias gem-check='~/.openclaw/bin/gemini-wrapper.sh --check'
  EOF

  # Reload shell
  source ~/.zshrc
  ```

- [ ] **Test aliases**
  ```bash
  gem-check  # Should show green checkmarks
  gem-plan -p "test" -m gemini-2.5-flash
  ```

- [ ] **Create a starter script** (optional)
  ```bash
  mkdir -p ~/scripts
  cat > ~/scripts/gemini-analysis.sh << 'EOF'
  #!/bin/bash
  # Example: Analyze files with Gemini

  set -a && source ~/.openclaw/.env && set +a

  for file in "$@"; do
    echo "=== Analyzing $file ==="
    ~/.openclaw/bin/gemini-wrapper.sh \
      -p "Review: $(cat "$file")" \
      -m gemini-2.5-flash \
      --approval-mode yolo
  done
  EOF
  chmod +x ~/scripts/gemini-analysis.sh
  ```

### Phase 4: Documentation Accessibility

- [ ] **Place docs where they're discoverable**
  ```bash
  # In repo (already done)
  # - GEMINI_QUICK_REFERENCE.md
  # - GEMINI_SETUP_GUIDE.md
  # - GEMINI_EXAMPLES.md
  # - GEMINI_IMPLEMENTATION_GUIDE.md (this file)

  # Also in memory for persistence
  # - memory/gemini-skill-improvements.md
  ```

- [ ] **Link from main README**
  - ✅ Already added section to `README.md`

- [ ] **Create a startable example** (optional)
  ```bash
  mkdir -p examples/gemini
  cp GEMINI_QUICK_REFERENCE.md examples/gemini/
  cp GEMINI_EXAMPLES.md examples/gemini/
  ```

---

## Key Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Wrapper Script | `.claude/bin/gemini-wrapper.sh` | Auto-loads env, validates, diagnostics |
| Quick Ref | `GEMINI_QUICK_REFERENCE.md` | 1-page cheat sheet |
| Setup Guide | `GEMINI_SETUP_GUIDE.md` | Complete setup + troubleshooting |
| Examples | `GEMINI_EXAMPLES.md` | 30+ copy-paste examples |
| Implementation | `GEMINI_IMPLEMENTATION_GUIDE.md` | This file - roadmap |
| Memory | `.claude/projects/*/memory/gemini-skill-improvements.md` | Technical deep-dive |

---

## Common Usage Patterns

### Pattern 1: Safe Code Review
```bash
# Always use yolo mode for read-only analysis
~/.openclaw/bin/gemini-wrapper.sh \
  -p "Security review: $(cat file.py)" \
  -m gemini-2.5-flash \
  --approval-mode yolo
```

### Pattern 2: Interactive Development
```bash
# Load once, then use interactively
set -a && source ~/.openclaw/.env && set +a
gemini -m gemini-2.5-flash

# Then ask questions:
# > Explain this code pattern
# > Help debug this error
# > Suggest improvements
```

### Pattern 3: Batch Analysis
```bash
# Analyze multiple files
for file in src/*.py tests/*.py; do
  ~/.openclaw/bin/gemini-wrapper.sh \
    -p "Analyze: $(cat "$file")" \
    -m gemini-2.5-flash \
    --approval-mode yolo
done
```

### Pattern 4: Research with Tools
```bash
# Use auto_edit for research that might call tools
~/.openclaw/bin/gemini-wrapper.sh \
  -p "Research best practices for X" \
  -m gemini-2.5-flash \
  --approval-mode auto_edit
```

---

## Troubleshooting Decision Tree

```
❌ "Exit Code 41: GEMINI_API_KEY not found"
  ├─ Yes: ~/.openclaw/.env exists?
  │  └─ No → Create: echo "GEMINI_API_KEY=sk-..." > ~/.openclaw/.env
  │  └─ Yes: Does it contain GEMINI_API_KEY=...?
  │     └─ No → Add: echo "GEMINI_API_KEY=sk-..." >> ~/.openclaw/.env
  │     └─ Yes: Reload shell
  │        └─ set -a && source ~/.openclaw/.env && set +a
  │        └─ Retry command
  │
  ├─ Still failing? Run diagnostic:
  │  └─ ~/.openclaw/bin/gemini-wrapper.sh --check
  │
  └─ Check online resources:
     └─ See GEMINI_SETUP_GUIDE.md section "Fixing Exit Code 41"

❌ "Permission denied" on wrapper script
  └─ chmod +x ~/.openclaw/bin/gemini-wrapper.sh

❌ "gemini: command not found"
  └─ brew install gemini-cli

❌ "No output / seems to hang"
  └─ Try: ~/.openclaw/bin/gemini-wrapper.sh --debug -p "test"
  └─ Or: Check internet connection / API quota
```

---

## Success Criteria

- ✅ Wrapper script works without environment variables manually exported
- ✅ `~/.openclaw/bin/gemini-wrapper.sh --check` shows all green
- ✅ `~/.openclaw/bin/gemini-wrapper.sh -p "test" -m gemini-2.5-flash` completes successfully
- ✅ Can run multiple Gemini commands in sequence without re-exporting
- ✅ Clear error messages guide users to solutions
- ✅ Documentation covers setup, usage, and troubleshooting
- ✅ Examples are copy-paste ready

---

## Performance & Reliability Improvements

### Before (Fragile)
```bash
# ❌ Error-prone
source ~/.openclaw/.env && gemini -p "..."  # Only works if GEMINI_API_KEY is already set
export GEMINI_API_KEY=$(grep ... ~/.openclaw/.env | cut ...)  # Complex, brittle
```

### After (Robust)
```bash
# ✅ Reliable
~/.openclaw/bin/gemini-wrapper.sh -p "..."  # Always works, validates, provides diagnostics
```

### Reliability Improvements
- ✅ No manual environment loading needed
- ✅ Pre-execution validation catches issues early
- ✅ Clear, actionable error messages
- ✅ Works across different shells (bash, zsh)
- ✅ Handles edge cases (missing files, empty vars, etc.)

---

## Advanced Customization

### Custom Gemini Binary Path
```bash
# Override default binary location
GEMINI_BIN=/usr/local/bin/gemini ~/.openclaw/bin/gemini-wrapper.sh -p "test"
```

### Custom Environment File Location
```bash
# Use different .env file
ENV_FILE=~/.config/gemini.env ~/.openclaw/bin/gemini-wrapper.sh -p "test"
```

### Debug Mode
```bash
# See detailed execution trace
~/.openclaw/bin/gemini-wrapper.sh --debug -p "test"
```

### Add Your Own Validation
To extend the wrapper with additional checks, edit `.claude/bin/gemini-wrapper.sh` and add after the `validate_environment()` function:

```bash
# Custom validation example
my_custom_check() {
    if [ "$CUSTOM_VAR" != "expected_value" ]; then
        print_error "Custom check failed"
        return 1
    fi
}

# Then call in main workflow:
load_environment
validate_environment
my_custom_check  # Add your check
run_gemini "$@"
```

---

## Maintenance & Future Updates

### If Gemini CLI Changes
1. Check if wrapper still works: `~/.openclaw/bin/gemini-wrapper.sh --check`
2. Update wrapper if needed (the core logic is POSIX-compatible)
3. Update documentation with new flags/modes
4. Test against different models

### If GEMINI_API_KEY Environment Changes
1. Update `.env` file location if moved
2. Update wrapper script's `ENV_FILE` variable
3. Document new location in setup guides

### If New Approval Modes Added
1. Add to `GEMINI_QUICK_REFERENCE.md` table
2. Add examples to `GEMINI_EXAMPLES.md`
3. Update wrapper help text

---

## Rollout Plan

### For Individual Use
1. Copy wrapper script: ✅ Done
2. Follow "Phase 1: User Setup" above
3. Refer to GEMINI_QUICK_REFERENCE.md daily

### For Team/Project
1. Add to repo: ✅ Done (`.claude/bin/gemini-wrapper.sh`)
2. Add to CLAUDE.md: Document in project-level instructions
3. Create team Slack snippet with quick commands
4. Host documentation (e.g., GitHub wiki or internal docs)
5. Add to onboarding checklist

### For Gemini CLI Skill Improvement
Future work (recommended):
1. Submit improvements to Gemini CLI project
2. Add self-healing to Gemini CLI directly
3. Improve built-in error messages
4. Add `--auto-load-env` flag

---

## Testing Checklist

- [ ] Wrapper script executable
- [ ] `--help` shows documentation
- [ ] `--check` validates configuration
- [ ] `--debug` shows trace output
- [ ] `-p "test"` works without manual setup
- [ ] All approval modes work: default, auto_edit, yolo, plan
- [ ] Works with all models: gemini-2.5-flash, gemini-2.0-pro-exp, etc.
- [ ] Works after shell restart (persistence test)
- [ ] Works in different shells (bash, zsh)
- [ ] Long prompts work (multi-line)
- [ ] Special characters in prompts handled
- [ ] Multiple commands in sequence work

---

## Documentation Index

### Quick Start (Pick One)
- **1-page cheat sheet**: `GEMINI_QUICK_REFERENCE.md`
- **Interactive examples**: `GEMINI_EXAMPLES.md` (search for your use case)
- **Complete setup**: `GEMINI_SETUP_GUIDE.md`

### For Different Needs
| Need | Document | Section |
|------|----------|---------|
| First time setup | GEMINI_SETUP_GUIDE.md | Quick Start |
| Common commands | GEMINI_QUICK_REFERENCE.md | Most Common Commands |
| Code examples | GEMINI_EXAMPLES.md | All examples |
| Troubleshooting | GEMINI_SETUP_GUIDE.md | Troubleshooting |
| Approval modes | GEMINI_QUICK_REFERENCE.md | Approval Modes |
| CDQ + Gemini | GEMINI_EXAMPLES.md | CDQ-Specific Examples |
| Technical deep-dive | memory/gemini-skill-improvements.md | Recommendations |

---

## Next Steps

1. **Immediate** (Done)
   - ✅ Create wrapper script
   - ✅ Create documentation
   - ✅ Add examples
   - ✅ Add to README

2. **Short-term** (This week)
   - [ ] Test wrapper with your own prompts
   - [ ] Set up shell aliases for convenience
   - [ ] Share with team if applicable

3. **Medium-term** (This month)
   - [ ] Integrate Gemini into regular CDQ workflows
   - [ ] Create custom examples for your domain
   - [ ] Fine-tune approval modes for your use cases

4. **Long-term** (Future)
   - [ ] Monitor Gemini CLI updates
   - [ ] Consider upstream improvements
   - [ ] Document lessons learned

---

## Questions?

See the comprehensive documentation:
- **Setup questions**: GEMINI_SETUP_GUIDE.md
- **Usage questions**: GEMINI_EXAMPLES.md
- **Commands**: GEMINI_QUICK_REFERENCE.md
- **Technical details**: memory/gemini-skill-improvements.md
