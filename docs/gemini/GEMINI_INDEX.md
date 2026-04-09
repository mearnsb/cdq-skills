# Gemini CLI Documentation Index

Complete guide to all Gemini CLI documentation and tools in this project.

## 🚀 Start Here

### For First-Time Users (5 minutes)
1. Read: **[GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md)** (1-page cheat sheet)
2. Add to `~/.zshrc`: `alias gsearch='~/.claude/bin/gemini-search'` then `source ~/.zshrc`
3. Try: `gsearch -p "Say hello"`

### For Detailed Setup (15 minutes)
1. Read: **[GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md)** (complete guide)
2. Choose your setup method (permanent or temporary)
3. Follow the troubleshooting guide if issues arise

### For Learning by Example (Copy & Paste Ready)
1. Browse: **[GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md)** (30+ examples)
2. Find your use case
3. Copy command and modify for your needs

---

## 📚 Documentation Files

### Beginner
| Document | Time | Purpose |
|----------|------|---------|
| [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md) | 1 min | Cheat sheet - most common commands |
| [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md#quick-start) | 5 min | Quick start section only |

### Intermediate
| Document | Time | Purpose |
|----------|------|---------|
| [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md) | 15 min | Full setup guide + troubleshooting |
| [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md) | 10 min | Browse relevant examples for your use case |

### Advanced
| Document | Time | Purpose |
|----------|------|---------|
| [GEMINI_IMPLEMENTATION_GUIDE.md](./GEMINI_IMPLEMENTATION_GUIDE.md) | 20 min | Implementation roadmap + customization |
| [memory/gemini-skill-improvements.md](../.claude/projects/-Users-brian-github-cdq-skills/memory/gemini-skill-improvements.md) | 15 min | Technical deep-dive into fix |

### Project Integration
| Document | Source |
|----------|--------|
| [README.md](./README.md#using-gemini-cli-with-cdq-skills) | Gemini summary in main README |
| [CLAUDE.md](./CLAUDE.md) | Project-level instructions |

---

## 🛠️ Tools & Scripts

| Tool | Location | Usage |
|------|----------|-------|
| **Main Script** | `~/.claude/bin/gemini-search` | Auto-loads API key, sets flash-lite + yolo defaults |
| **Alias (Recommended)** | `gsearch` (if configured) | `gsearch -p "prompt"` |
| **Direct Path** | `~/.claude/bin/gemini-search` | `~/.claude/bin/gemini-search -p "prompt"` |
| **Help** | `gemini --help` | Show Gemini CLI help |

---

## 🎯 Common Tasks

### Task: Set Up Gemini for First Time
→ [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md#quick-start)

### Task: Fix "Exit Code 41" Error
→ [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md#fixing-exit-code-41-error)

### Task: Review Code with Gemini
→ [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md#code-review-examples)

### Task: Use Gemini for CDQ Planning
→ [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md#cdq-specific-examples)

### Task: Create Custom Aliases
→ [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md#create-aliases-optional)

### Task: Debug Gemini Issues
→ [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md#troubleshooting)

### Task: Learn Approval Modes
→ [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md#approval-modes)

---

## 📋 Document Structure

### GEMINI_QUICK_REFERENCE.md
- TL;DR 30-second setup
- Most common commands
- Approval modes (table)
- Models reference
- Common file input tricks
- Troubleshooting quick fixes
- Aliases setup
- Key files reference

### GEMINI_SETUP_GUIDE.md
- Quick Start (3 parts)
- Common Usage Examples (4 examples)
- Fixing Exit Code 41 (3 solutions)
- Wrapper Script Setup (3 steps)
- Approval Modes (table + examples)
- Model Selection
- Troubleshooting (4 issues)
- Integration with Claude Code
- Best Practices (5 principles)

### GEMINI_EXAMPLES.md
- Setup Examples (3)
- Code Review Examples (3)
- Analysis Examples (3)
- Development Examples (3)
- CDQ-Specific Examples (3)
- Integration Examples (3)
- Interactive Mode Examples (2)
- Approval Mode Examples (3)
- Troubleshooting Examples (3)
- Real-World Workflows (3)
- Tips & Tricks (4)

### GEMINI_IMPLEMENTATION_GUIDE.md
- Executive Summary
- Implementation Checklist (4 phases)
- Key Files Reference
- Common Usage Patterns (4)
- Troubleshooting Decision Tree
- Success Criteria
- Performance & Reliability Improvements
- Advanced Customization
- Maintenance & Future Updates
- Rollout Plan
- Testing Checklist
- Documentation Index
- Next Steps

---

## 🔍 Find What You Need

### By Situation

**"I just installed Gemini CLI"**
→ Start with [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md)

**"I got Exit Code 41 error"**
→ Go to [GEMINI_SETUP_GUIDE.md#fixing-exit-code-41-error](./GEMINI_SETUP_GUIDE.md#fixing-exit-code-41-error)

**"I want to review code"**
→ See [GEMINI_EXAMPLES.md#code-review-examples](./GEMINI_EXAMPLES.md#code-review-examples)

**"I need a copy-paste example"**
→ Browse [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md) for your use case

**"I want to set permanent setup"**
→ Read [GEMINI_SETUP_GUIDE.md#wrapper-script-setup](./GEMINI_SETUP_GUIDE.md#wrapper-script-setup)

**"I want to understand the fix"**
→ Read [memory/gemini-skill-improvements.md](../.claude/projects/-Users-brian-github-cdq-skills/memory/gemini-skill-improvements.md)

**"I need to plan implementation for my team"**
→ Use [GEMINI_IMPLEMENTATION_GUIDE.md](./GEMINI_IMPLEMENTATION_GUIDE.md)

### By Document Length

**1 page** → [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md)

**5 pages** → [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md)

**10+ pages** → [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md) or [GEMINI_IMPLEMENTATION_GUIDE.md](./GEMINI_IMPLEMENTATION_GUIDE.md)

### By Time Available

**2 minutes** → [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md#tldr---30-second-setup)

**5 minutes** → [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md#quick-start) + test

**15 minutes** → Full [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md) with setup

**30 minutes** → Browse [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md) by use case

**1 hour** → Full deep-dive with [GEMINI_IMPLEMENTATION_GUIDE.md](./GEMINI_IMPLEMENTATION_GUIDE.md)

---

## 💡 Pro Tips

1. **Use the gsearch Alias**: Minimal typing, all defaults baked in — `gsearch -p "query"`
2. **Leverage Defaults**: flash-lite + yolo are pre-configured — override only when needed
3. **Web Search**: Just ask — "Search the web for..." is automatically handled
4. **See Tool Calls**: `gsearch -p "..." --approval-mode auto_edit` to watch execution
5. **Stronger Model**: `gsearch -p "..." -m gemini-2.5-flash` for complex reasoning tasks

---

## 🐛 Troubleshooting Flowchart

```
Is it broken?
│
├─ Exit Code 41 (API key not found)
│  └─ Read: Fixing Exit Code 41 in GEMINI_SETUP_GUIDE.md
│
├─ Permission denied (wrapper script)
│  └─ Run: chmod +x ./.claude/bin/gemini-wrapper.sh
│
├─ gemini: command not found
│  └─ Run: brew install gemini-cli
│
├─ Something else
│  └─ Run: ./.claude/bin/gemini-wrapper.sh --check --debug
│  └─ Read: Troubleshooting section in GEMINI_SETUP_GUIDE.md
│
└─ Still stuck?
   └─ Check: memory/gemini-skill-improvements.md
   └─ Read: GEMINI_IMPLEMENTATION_GUIDE.md#troubleshooting-decision-tree
```

---

## 📖 Reading Paths

### Path A: "Just Make It Work" (5 minutes)
1. [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md#tldr---30-second-setup) - TL;DR section
2. Run: `./.claude/bin/gemini-wrapper.sh --check`
3. Go use it!

### Path B: "I Want Full Setup" (20 minutes)
1. [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md#quick-start) - Full guide
2. [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md) - Bookmark this
3. Run: tests from [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md#wrapper-script-setup#step-3-test-it-works)

### Path C: "Show Me Examples" (15 minutes)
1. [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md) - Browse by topic
2. Find your use case
3. Copy & modify for your needs

### Path D: "I Need to Understand This" (1 hour)
1. [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md) - Full context
2. [memory/gemini-skill-improvements.md](../.claude/projects/-Users-brian-github-cdq-skills/memory/gemini-skill-improvements.md) - Technical analysis
3. [GEMINI_IMPLEMENTATION_GUIDE.md](./GEMINI_IMPLEMENTATION_GUIDE.md) - Implementation details

---

## 🎓 Learning Resources

### External Resources
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Get API Key](https://aistudio.google.com/apikey)

### Internal Resources
- [README.md](./README.md) - CDQ Skills overview
- [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md) - CDQ workflow examples
- [SETUP.md](./SETUP.md) - Project setup

---

## 📞 Quick Contact

- **Quick questions?** → [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md)
- **Setup issues?** → [GEMINI_SETUP_GUIDE.md#troubleshooting](./GEMINI_SETUP_GUIDE.md#troubleshooting)
- **Need examples?** → [GEMINI_EXAMPLES.md](./GEMINI_EXAMPLES.md)
- **Technical details?** → [memory/gemini-skill-improvements.md](../.claude/projects/-Users-brian-github-cdq-skills/memory/gemini-skill-improvements.md)
- **Implementation help?** → [GEMINI_IMPLEMENTATION_GUIDE.md](./GEMINI_IMPLEMENTATION_GUIDE.md)

---

## ✅ Verification Checklist

Before moving on, verify:

- [ ] Read: [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md) (2 min)
- [ ] Run: `./.claude/bin/gemini-wrapper.sh --check` (should show ✅ checks)
- [ ] Test: `./.claude/bin/gemini-wrapper.sh -p "Say hello" -m gemini-2.5-flash`
- [ ] Setup: Choose permanent or temporary setup from [GEMINI_SETUP_GUIDE.md](./GEMINI_SETUP_GUIDE.md)
- [ ] Bookmark: Save [GEMINI_QUICK_REFERENCE.md](./GEMINI_QUICK_REFERENCE.md) for daily use

---

## File Locations Summary

```
cdq-skills/
├── GEMINI_INDEX.md                 ← You are here
├── GEMINI_QUICK_REFERENCE.md       ← 1-page cheat sheet (START HERE)
├── GEMINI_SETUP_GUIDE.md           ← Complete setup guide
├── GEMINI_EXAMPLES.md              ← 30+ copy-paste examples
├── GEMINI_IMPLEMENTATION_GUIDE.md  ← Implementation roadmap
├── README.md                        ← Main project README
├── .claude/bin/
│   ├── gemini-search               ← Main script (auto defaults)
│   └── gemini-wrapper.sh.deprecated ← Old version (archived)
├── .claude/skills/gemini/
│   └── SKILL.md                     ← Claude Code skill docs
└── memory/
    └── gemini-skill-improvements.md ← Technical analysis
```

---

Last Updated: 2026-04-08
