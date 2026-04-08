# GitHub Readiness Plan - CDQ Skills Repository

**Status:** Planning Stage
**Target:** Prepare for GitHub publication
**Date Started:** 2026-04-08

---

## 📋 Executive Summary

This document outlines the complete process to prepare the CDQ Skills monorepository for GitHub publication. The project is a well-structured collection of 17 Collibra DQ skills with clean dependencies and comprehensive documentation. Main work involves:

- Removing sensitive credentials and development artifacts
- Consolidating platform-specific duplicates
- Validating self-contained skill bundles
- Adding public-ready documentation

**Estimated effort:** 1-2 hours
**Risk level:** Low (all changes are removals/cleanups, not rewrites)

---

## 🎯 Success Criteria

✅ No secrets, credentials, or tokens in tracked files
✅ All development artifacts cleaned up
✅ All skills validated as self-contained
✅ Comprehensive setup documentation
✅ Test suite passing cleanly
✅ MIT License applied
✅ Validation script confirms readiness

---

## 🔄 Phase Breakdown

### PHASE 1: Audit & Content Review (Review Only)
**Objective:** Identify all content that needs attention before cleanup
**Time:** 20 minutes
**Risk:** None (read-only)

#### Step 1.1: Content Audit for Secrets
- Scan all `.py` files for hardcoded credentials
- Search for API keys, tokens, endpoints in code
- Check documentation for workspace paths
- Look for environment variable examples with real values

**Expected output:** List of files with potential issues

#### Step 1.2: Workspace Path Audit
- Grep for "/Users/brian" in all files
- Search for workspace-specific references
- Find references to local .env or config files
- Check for project-specific paths in examples

**Expected output:** List of files containing workspace paths

#### Step 1.3: .env File Security Review
- Review contents vs requirements
- Verify all values should be in example file
- Check for production credentials
- Confirm cleanup is safe

**Expected output:** Safe to remove? [YES/NO]

#### Step 1.4: Modified Files Assessment
- Review each file modified since last commit
- Determine: keep changes, discard, or commit?
- Check if changes are work-in-progress or final

**Expected output:** Decision matrix for each file

#### Step 1.5: Untracked Directories Assessment
- Review `.claude/skills/auto-cdq/`
- Assess `plans/` directory contents
- Determine if these are active development or archived

**Expected output:** Keep/archive/remove decision for each

---

### PHASE 2: Environment & Secrets Cleanup (Execute)
**Objective:** Remove all sensitive data from repository
**Time:** 10 minutes
**Risk:** Low (removing secrets is always safe)

#### Step 2.1: Backup Current .env
```bash
cp .env .env.backup
```

#### Step 2.2: Review .env.example
- Verify it's safe for public consumption
- All values are non-sensitive examples
- All required variables are documented

#### Step 2.3: Remove .env File
```bash
rm .env
git rm --cached .env  # If already tracked
```

#### Step 2.4: Verify .gitignore Coverage
```bash
git check-ignore .env
# Should output: .env
```

#### Step 2.5: Confirm Cleanup
```bash
git status | grep "\.env"
# Should show nothing related to .env
```

---

### PHASE 3: Development Artifacts Removal (Execute)
**Objective:** Clean up session-specific and work-in-progress files
**Time:** 15 minutes
**Risk:** Low (removing untracked/session files)

#### Step 3.1: Assess and Handle Modified Files
For each modified file (from Phase 1 output):

**Option A: Keep Working Changes**
```bash
git add <file>
```

**Option B: Discard Changes**
```bash
git checkout <file>
```

**Option C: Backup and Discard**
```bash
cp <file> <file>.backup
git checkout <file>
```

#### Step 3.2: Clean Untracked Development Directories

**For `.claude/skills/auto-cdq/`:**
- Is this active work? → Keep as `.claude/skills/auto-cdq/`
- Is this archived? → Move to `.claude/skills/archive/auto-cdq/`
- Is this temporary? → Remove completely

**Action:** [TO BE DETERMINED in Phase 1 review]

**For `plans/` directory:**
- Contains session-specific planning states
- Not needed for repository
- Should be in .gitignore or removed

**Action:**
```bash
rm -rf plans/
# Add to .gitignore if not present
echo "plans/" >> .gitignore
```

#### Step 3.3: Verify .claude/projects/ is .gitignored
```bash
git check-ignore -v .claude/projects/
# Should output: .claude/projects/	.gitignore
```

#### Step 3.4: Clean Workspace-Specific Files
Remove any `.claude/settings.local.json` overrides:
- Already in .gitignore ✓
- Verify: `git check-ignore .claude/settings.local.json`

#### Step 3.5: Verify Clean Status
```bash
git status
# Should show: nothing to commit, working tree clean
# (Or only intentional changes)
```

---

### PHASE 4: Repository State Cleanup (Execute if needed)
**Objective:** Commit or discard modifications
**Time:** 10 minutes
**Risk:** Medium (committing work changes)

#### Step 4.1: Review Modified Files

Current modified files:
- `.claude/skills/cdq-get-jobs/lib/client.py`
- `.claude/skills/lib/skill_wrapper.py`
- `.gitignore`
- `lib/client.py`

For each file:

**Check what changed:**
```bash
git diff <file>
```

**Decision matrix:**
- Is this a bug fix? → Commit as feature fix
- Is this an enhancement? → Commit as feature
- Is this a work-in-progress? → Stash or commit as WIP
- Is this a mistake? → Discard (git checkout)

#### Step 4.2: Stage Intentional Changes
```bash
git add <file>  # For each intentional change
```

#### Step 4.3: Create Commit
```bash
git commit -m "Prepare for GitHub: update skill wrappers and .gitignore"
```

#### Step 4.4: Verify Clean Status
```bash
git status
# Should be clean
```

---

### PHASE 5: Platform & Skill Consolidation (Review & Decide)
**Objective:** Reconcile .claude/ and .gemini/ skill duplicates
**Time:** 20 minutes
**Risk:** Low (review and categorize)

#### Step 5.1: Audit Platform Differences
```bash
# Count skills in each platform
find .claude/skills -name "SKILL.md" | wc -l
find .gemini/skills -name "SKILL.md" | wc -l
```

**Options:**
1. **Keep Both Platforms:** Document how to link to each platform
   - Update README with platform-specific setup
   - Verify both are kept in sync
   - Add note about platform differences

2. **Standardize on .claude/:** Remove .gemini/
   - Simplify repository
   - Users can link/copy as needed
   - Reduce maintenance

3. **Symlink Approach:** .gemini/ links to .claude/
   - Avoid duplication
   - Ensure consistency
   - Platform agnostic

**Decision:** [TO BE DECIDED - see Phase 1.5]

#### Step 5.2: Verify Skill Parity
If keeping both:
```bash
# Compare skill counts
echo ".claude: $(find .claude/skills -name SKILL.md | wc -l)"
echo ".gemini: $(find .gemini/skills -name SKILL.md | wc -l)"

# Should be equal if we're keeping both updated
```

#### Step 5.3: Document Platform Support

**Add to README.md:**
```markdown
## Platform Support

- **Claude Code (.claude/skills/)** - Primary platform
- **Gemini CLI (.gemini/skills/)** - Secondary (auto-synced)
- **Other platforms** - Direct Python CLI usage supported

For linking or copying to other platforms, see SETUP.md
```

---

### PHASE 6: Dependencies & Configuration (Update)
**Objective:** Ensure clean, well-documented setup
**Time:** 15 minutes
**Risk:** Very Low (documentation updates only)

#### Step 6.1: Verify requirements.txt
Current:
```
python-dotenv>=1.0.0
requests>=2.31.0
```

**Action:** Confirm this is complete
```bash
python -m pip check  # After installing from requirements.txt
```

#### Step 6.2: Create SETUP.md

Create `/Users/brian/github/cdq-skills/SETUP.md` with:

```markdown
# Setup Guide - CDQ Skills

## Prerequisites
- Python 3.8+
- pip or conda
- Access to Collibra DQ instance

## Installation

### Option 1: Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Option 2: Development Installation
\`\`\`bash
pip install -r requirements.txt
pip install -e .
\`\`\`

## Configuration

### 1. Create .env File
\`\`\`bash
cp .env.example .env
\`\`\`

### 2. Fill in Credentials
Edit `.env` with your Collibra DQ details:

| Variable | Description | Example |
|----------|-------------|---------|
| `DQ_URL` | Collibra DQ API base URL | `https://collibra.mycompany.com` |
| `DQ_USERNAME` | CDQ username | `api_user@company.com` |
| `DQ_PASSWORD` | CDQ password | `YourSecurePassword123!` |
| `DQ_ISS` | Tenant identifier | `my_tenant` |
| `DQ_CXN` | Default connection | `BIGQUERY` (or `SNOWFLAKE`, etc.) |
| `DQ_VERIFY_SSL` | SSL verification | `true` (set to `false` for self-signed certs) |

### 3. Test Connection
\`\`\`bash
python lib/client.py test-connection
\`\`\`

## Usage

### Direct Python CLI
\`\`\`bash
python lib/client.py <command> --args
\`\`\`

### Claude Code
```bash
/cdq-search-catalog --query ""
/cdq-run-sql --sql "SELECT COUNT(*) FROM table"
```

### Gemini CLI
\`\`\`bash
cdq-search-catalog --query ""
cdq-run-sql --sql "SELECT COUNT(*) FROM table"
\`\`\`

## Troubleshooting

### Connection Errors
- Verify `DQ_URL` is reachable
- Check credentials in `.env`
- Confirm `DQ_ISS` (tenant) is correct

### SSL Errors
- Check if CDQ uses self-signed certificates
- Set `DQ_VERIFY_SSL=false` in `.env`

### Command Not Found
- Ensure dependencies installed: `pip install -r requirements.txt`
- For Claude Code: verify skills linked in `.claude/skills/`
- For Gemini CLI: verify skills linked in `.gemini/skills/`

## First-Time Workflows

See [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md) for multi-step workflows with examples.

Quick start:
\`\`\`bash
# 1. Search for a table
python lib/client.py search-catalog --query "customer"

# 2. Preview data (safe limit)
python lib/client.py run-sql --sql "SELECT * FROM samples.customers LIMIT 5"

# 3. Register a dataset
python lib/client.py run-dq-job \
  --dataset "MY_CUSTOMERS" \
  --sql "SELECT * FROM samples.customers LIMIT 10000"

# 4. Check results
python lib/client.py get-results --dataset "MY_CUSTOMERS" --run-id "2026-04-08"
\`\`\`
```

#### Step 6.3: Update README with Setup Reference
Add link to SETUP.md:
```markdown
## Quick Start

1. [Installation & Setup](./SETUP.md)
2. Configure `.env` with your Collibra DQ credentials
3. Test: `python lib/client.py test-connection`
4. See [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md) for workflows
```

---

### PHASE 7: License & Documentation (Create)
**Objective:** Add MIT License and finalize public-ready docs
**Time:** 10 minutes
**Risk:** Very Low (adding files)

#### Step 7.1: Create LICENSE File

Create `/Users/brian/github/cdq-skills/LICENSE`:

```
MIT License

Copyright (c) 2026 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### Step 7.2: Add License Reference to README
Add to top of README.md:
```markdown
...
> **Security Note:** This client uses standard environment variables...

## License

MIT License - See [LICENSE](./LICENSE) for details
```

#### Step 7.3: Create CONTRIBUTING.md (Optional)

```markdown
# Contributing to CDQ Skills

We welcome contributions! Here's how to help:

## Skill Development

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-skill`
3. Follow the skill structure in `.claude/skills/cdq-*/`
4. Test thoroughly with `python tests/test_skills.py`
5. Submit a pull request

## Skill Structure

Each skill must include:
- `SKILL.md` - Documentation and usage examples
- `lib/client.py` - Wrapper using shared skill_wrapper module
- Consistent argument naming and error handling

## Testing

All skills must pass:
```bash
python tests/test_skills.py
```

## Documentation

- Update README.md for major features
- Add examples to EXAMPLE_PROMPTS.md
- Document breaking changes

## Code Style

- Follow PEP 8
- Use type hints where possible
- Include docstrings for complex functions

## Questions?

Open an issue on GitHub or check existing documentation in EXAMPLE_PROMPTS.md.
```

---

### PHASE 8: Final Validation & Testing (Execute)
**Objective:** Confirm readiness for GitHub publication
**Time:** 15 minutes
**Risk:** Very Low (validation only)

#### Step 8.1: Run Test Suite
```bash
python tests/test_skills.py
```

**Expected output:**
```
Ran 22 tests in X.XXXs
OK
```

#### Step 8.2: Verify No Secrets Staged
```bash
# Check for any sensitive files
git status --porcelain | grep -E "\.(env|key|pem|secrets)$"
# Should output: nothing

# Verify .gitignore working
git check-ignore -v .env
# Should output: .env	.gitignore
```

#### Step 8.3: Dry-Run Git Add
```bash
git add --dry-run .
# Review files - should not include:
# - .env
# - credentials
# - personal data
# - workspace paths
```

#### Step 8.4: Run Validation Script
```bash
python scripts/validate_github_readiness.py
# Will be created in Phase 8.5
```

**Expected output:**
```
✅ No hardcoded credentials found
✅ No workspace paths detected
✅ All skills validated as self-contained
✅ Test suite passing
✅ No sensitive files in git index
✅ Repository ready for GitHub!
```

#### Step 8.5: Generate Readiness Report
```bash
echo "GitHub Readiness Report - $(date)" > READINESS_REPORT.txt
echo "" >> READINESS_REPORT.txt
echo "Automated Checks:" >> READINESS_REPORT.txt
python scripts/validate_github_readiness.py >> READINESS_REPORT.txt
```

---

## 🛠️ Automated Validation Script

**File:** `scripts/validate_github_readiness.py`

```python
#!/usr/bin/env python3
"""
Validate CDQ Skills repository for GitHub readiness.

Checks:
1. No hardcoded credentials
2. No workspace paths
3. Skills are self-contained
4. Tests passing
5. No sensitive files
"""

import os
import re
import subprocess
import sys
from pathlib import Path

class ReadinessValidator:
    def __init__(self, repo_root="."):
        self.repo_root = Path(repo_root)
        self.issues = []
        self.warnings = []
        self.passed = []

    def check_no_credentials(self):
        """Scan for hardcoded secrets."""
        patterns = [
            r'(api_key|apikey|api[-_]?key)\s*=\s*["\']?[a-zA-Z0-9]+["\']?',
            r'(password|passwd|pwd)\s*=\s*["\']?[a-zA-Z0-9_.!@#$%]+["\']?',
            r'(token|auth[-_]?token)\s*=\s*["\']?[a-zA-Z0-9_.-]+["\']?',
            r'Bearer\s+[a-zA-Z0-9_.-]+',
            r'https?://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+@',
        ]

        sensitive_files = []
        for py_file in self.repo_root.rglob("*.py"):
            if ".git" in str(py_file):
                continue
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        sensitive_files.append(str(py_file))
                        break
            except Exception as e:
                print(f"Warning: Could not scan {py_file}: {e}")

        if sensitive_files:
            self.issues.append(f"Potential credentials found in: {', '.join(sensitive_files)}")
        else:
            self.passed.append("✅ No hardcoded credentials detected")

    def check_workspace_paths(self):
        """Check for workspace-specific paths."""
        workspace_marker = "/Users/brian"
        found_paths = []

        for file_type in ["*.py", "*.md", "*.txt"]:
            for text_file in self.repo_root.rglob(file_type):
                if ".git" in str(text_file):
                    continue
                try:
                    if workspace_marker in text_file.read_text():
                        found_paths.append(str(text_file))
                except Exception:
                    pass

        if found_paths:
            self.issues.append(f"Workspace paths found in: {', '.join(found_paths)}")
        else:
            self.passed.append("✅ No workspace-specific paths detected")

    def check_gitignore_coverage(self):
        """Verify .gitignore includes sensitive patterns."""
        gitignore = self.repo_root / ".gitignore"
        if not gitignore.exists():
            self.warnings.append("⚠️  .gitignore file not found")
            return

        required_patterns = [".env", "*.key", "*.pem", "__pycache__"]
        content = gitignore.read_text()
        missing = [p for p in required_patterns if p not in content]

        if missing:
            self.warnings.append(f"Missing patterns in .gitignore: {missing}")
        else:
            self.passed.append("✅ .gitignore has required patterns")

    def check_env_file_exists(self):
        """Verify .env does NOT exist (credentials should not be tracked)."""
        env_file = self.repo_root / ".env"
        if env_file.exists():
            self.issues.append(".env file exists - should be removed before push")
        else:
            self.passed.append("✅ .env file not present")

    def check_skills_self_contained(self):
        """Verify all skills have required files."""
        skills_dir = self.repo_root / ".claude" / "skills"
        missing_structure = []

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue

            skill_md = skill_dir / "SKILL.md"
            client_py = skill_dir / "lib" / "client.py"

            if not skill_md.exists():
                missing_structure.append(f"{skill_dir.name}: missing SKILL.md")
            if not client_py.exists():
                missing_structure.append(f"{skill_dir.name}: missing lib/client.py")

        if missing_structure:
            self.warnings.append(f"Skills with incomplete structure: {missing_structure}")
        else:
            skill_count = len([x for x in skills_dir.iterdir() if x.is_dir()])
            self.passed.append(f"✅ All {skill_count} skills have required structure")

    def check_tests_pass(self):
        """Run test suite."""
        try:
            result = subprocess.run(
                ["python", "tests/test_skills.py"],
                cwd=self.repo_root,
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                self.passed.append("✅ Test suite passing")
            else:
                self.issues.append(f"Tests failed:\n{result.stderr.decode()}")
        except Exception as e:
            self.warnings.append(f"Could not run tests: {e}")

    def validate(self):
        """Run all checks."""
        print("🔍 Validating CDQ Skills repository for GitHub readiness...\n")

        self.check_no_credentials()
        self.check_workspace_paths()
        self.check_gitignore_coverage()
        self.check_env_file_exists()
        self.check_skills_self_contained()
        self.check_tests_pass()

        # Print results
        if self.passed:
            print("✅ Passed Checks:")
            for check in self.passed:
                print(f"  {check}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warn in self.warnings:
                print(f"  {warn}")

        if self.issues:
            print("\n❌ Issues (must fix):")
            for issue in self.issues:
                print(f"  {issue}")
            return False
        else:
            print("\n" + "=" * 50)
            print("✅ Repository is ready for GitHub!")
            print("=" * 50)
            return True

if __name__ == "__main__":
    validator = ReadinessValidator()
    success = validator.validate()
    sys.exit(0 if success else 1)
```

---

## 📊 Checklist for Execution

### Before Starting
- [ ] Backup current state: `git stash`
- [ ] Confirm you're on main branch: `git branch`
- [ ] No uncommitted work you want to keep? (or backed up)

### Phase 1: Execute Audit
- [ ] Check for hardcoded credentials
- [ ] Check for workspace paths
- [ ] Review modified files
- [ ] Review untracked directories
- [ ] Determine action for auto-cdq/
- [ ] Determine action for plans/

### Phase 2: Cleanup Secrets
- [ ] Backup .env → .env.backup
- [ ] Remove .env file
- [ ] Verify .gitignore coverage
- [ ] Confirm .env removed from git

### Phase 3: Remove Artifacts
- [ ] Handle auto-cdq/ (keep/archive/remove)
- [ ] Remove or ignore plans/
- [ ] Clean up modified files
- [ ] Verify clean git status

### Phase 4: Cleanup Repository State
- [ ] Review each modified file
- [ ] Commit or discard each
- [ ] Final git status clean

### Phase 5: Platform Consolidation
- [ ] Audit .claude/ vs .gemini/
- [ ] Decide consolidation strategy
- [ ] Document approach in README

### Phase 6: Dependencies & Setup
- [ ] Verify requirements.txt complete
- [ ] Create SETUP.md
- [ ] Update README with links
- [ ] Document all environment variables

### Phase 7: License & Docs
- [ ] Add LICENSE file (MIT)
- [ ] Create CONTRIBUTING.md (optional)
- [ ] Update README with license reference
- [ ] Verify all MDfiles are GitHub-friendly

### Phase 8: Final Validation
- [ ] Run test suite: `python tests/test_skills.py`
- [ ] Run validation script: `python scripts/validate_github_readiness.py`
- [ ] Dry-run git add
- [ ] Generate readiness report
- [ ] Confirm all checks pass

### Ready for GitHub!
- [ ] All phases complete
- [ ] All tests passing
- [ ] Validation script confirms readiness
- [ ] Documentation complete
- [ ] Ready to: `git remote add origin <url> && git push -u origin main`

---

## 📝 Decision Matrix

### auto-cdq/ Directory
- **Keep**: Active development, add to .gitignore if work-in-progress
- **Archive**: Move to `.claude/skills/archive/auto-cdq/`
- **Remove**: If temporary and no longer needed

**Current Status**: [NEEDS REVIEW - Phase 1]

### .gemini/ Directory
- **Option A**: Keep both - .claude/ primary, .gemini/ secondary
  - Action: Verify parity, document setup
- **Option B**: Remove - GitHub only has .claude/
  - Action: Delete .gemini/, users link to .claude/
- **Option C**: Symlink - .gemini/ links to .claude/
  - Action: Create symlinks instead of copies

**Current Status**: [NEEDS REVIEW - Phase 1]

### Modified Files Actions
| File | Current Status | Action |
|------|---|---|
| `.claude/skills/cdq-get-jobs/lib/client.py` | Modified | [REVIEW Phase 1] |
| `.claude/skills/lib/skill_wrapper.py` | Modified | [REVIEW Phase 1] |
| `.gitignore` | Modified | [REVIEW Phase 1] |
| `lib/client.py` | Modified | [REVIEW Phase 1] |

---

## 🚀 Next: Phase 1 Execution

Proceed to **Phase 1: Audit & Content Review** in the next message.

