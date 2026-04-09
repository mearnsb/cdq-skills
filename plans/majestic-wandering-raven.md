# Plan: Default Gemini CLI to YOLO mode

## Context
The user wants the `gemini-wrapper.sh` script to always use `--approval-mode yolo` by default, unless another mode is explicitly specified. This avoids having to manually add the flag every time they want to use the tool in an automated or "unattended" fashion.

## Proposed Implementation
I will modify the `run_gemini` function in `/Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh`.

The logic will be:
1. Check if `--approval-mode` or `-m` (for model) is already in the arguments.
2. If `--approval-mode` is NOT present in the arguments, append `--approval-mode yolo` to the arguments list before executing the `gemini` binary.
3. I will also ensure that the default model is still handled correctly if not provided.

## Files to Modify
- `/Users/brian/github/cdq-skills/.claude/bin/gemini-wrapper.sh`

## Verification Plan
1. Run the script with a simple prompt without specifying any mode:
   `./gemini-wrapper.sh -p "test"`
   Check (using `--debug`) if `--approval-mode yolo` is included in the final command.
2. Run the script with an explicit mode:
   `./gemini-wrapper.sh -p "test" --approval-mode plan`
   Check (using `--debug`) if it respects the `plan` mode and does NOT add `yolo`.
3. Run the script with an explicit model:
   `./gemini-wrapper.sh -p "test" -m gemini-1.5-pro`
   Check if it still adds `--approval-mode yolo`.