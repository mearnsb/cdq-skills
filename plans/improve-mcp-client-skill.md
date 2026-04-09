# Plan: Improve and Simplify mcp-client Skill

## Context
The user wants to simplify the usage of the `mcp-client` skill and improve its documentation to avoid confusion. Currently, executing the skill requires manually `cd`-ing into the skill's directory before running the python command, because the script uses relative paths or expects to be run from its own directory. This caused confusion when the skill was initially invoked from the project root.

The goal is to:
1.  **Simplify usage**: Allow the skill to be called from anywhere without requiring a manual `cd`.
2.  **Improve Documentation**: Update the `SKILL.md` to accurately reflect the correct way to call the skill and provide clearer examples.
3.  **Future-proofing**: Ensure that the skill is robust and easy for both humans and agents to use.

## Proposed Implementation Strategy

### 1. Technical Improvement (The "Simplify" part)
Instead of requiring a `cd`, we can modify how the skill is invoked or how the script itself handles paths.
- **Option A (Update Skill Wrapper)**: If the skill is called via the `Skill` tool, we might need to ensure the environment or the way the command is constructed handles the directory correctly.
- **Option B (Update Python Script)**: Modify `mcp_client.py` to use absolute paths for its internal logic or relative to its own location (`__file__`).
- **Option C (Standardize Command Construction)**: Update the instructions/documentation to always recommend the full path or a specific way to invoke it that doesn't rely on the current working directory.

### 2. Documentation Update (The "Reflect accurately" part)
- Update `.claude/skills/mcp-client/SKILL.md`.
- Clearly state the "Correct Way to Call" the skill.
- Provide a "One-liner" example that works from the project root.

## Critical Files
- `.claude/skills/mcp-client/SKILL.md`
- `.claude/skills/mcp-client/scripts/mcp_client.py` (if code changes are needed)

## Verification Plan
1.  **Test current failure**: Try calling `python .claude/skills/mcp-client/scripts/mcp_client.py servers` from the project root and confirm it fails (if it still does).
2.  **Test improvement**: Call the improved version from the project root and confirm it succeeds.
3.  **Test documentation**: Verify that the new `SKILL.md` is clear and follows the recommended usage.