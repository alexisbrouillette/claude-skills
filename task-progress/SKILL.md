---
name: task-progress
description: Show the user live progress of any long-running task in a separate terminal window (title, description, progress bar, elapsed/ETA, current step, recent log). Use EVERY time you start a task expected to take more than ~30 seconds or run in the background: builds, test suites, data pipelines, installs, migrations, large refactors, Antigravity/agent delegations. Also use when the user asks to see progress or to demo it.
---

# Task progress viewer

The user cannot easily follow progress while waiting. For any long task, open a live viewer
in its own terminal and keep it updated. Script: `~/.claude/skills/task-progress/scripts/progress.py`
(stdlib Python 3, no install). Below, `PP="python3 ~/.claude/skills/task-progress/scripts/progress.py"`.

## Workflow

1. **Init** a state file in the scratchpad (not the project): `$PP init "$F" --title "Short name" --desc "One line on what and why"`
   (`F=<scratchpad>/progress-<task>.json`).
2. **Open the viewer**: `$PP open "$F"` (launches a new terminal window: gnome-terminal, kitty, alacritty, konsole or xterm).
   If it prints that no GUI terminal was found, give the user the printed `watch` command to paste in their terminal (e.g. the VS Code one).
3. **Update at every milestone**, cheaply and often (each call is instant):
   `$PP set "$F" --percent 40 --step "What is happening right now" --log "Notable event"`
   - `--percent` only when you genuinely know it (steps done / total, files processed / total). Omit it for an
     indeterminate animated bar; never invent numbers. Update `--step` even when percent is unknown.
   - `--step` = present-tense plain language ("Running tests: 3 of 8 suites"). `--log` = short past-tense events.
4. **Finish**: `$PP done "$F" --msg "Result in one line"` or `$PP fail "$F" --msg "What went wrong"`. Always call one of them, even on error.
   The viewer stays open until the user presses Ctrl-C.

For a shell command running in the background, wrap the steps around it: init, open, start it with
`run_in_background`, and update from its output while polling (use Monitor / periodic reads, not sleep loops).
If the task has natural phases, split percent ranges across them (e.g. 0-25, 25-60, ...).

## Rules
- Open the viewer once per task, before the work starts. Do not spawn a window for quick tasks.
- Keep the chat itself brief while it runs; the viewer carries the detail.
- Do not put secrets in `--desc`, `--step` or `--log`: they are shown on screen.

## Demo
`python3 ~/.claude/skills/task-progress/scripts/progress.py demo` runs a ~15 s simulated task in the current terminal.

## If this skill breaks (bug, crash, wrong platform)

These scripts were written and tested on Linux only; Windows/macOS users may hit problems
(`python3` vs `python`, bash missing, terminal launch, ANSI colors, paths).
1. Stop, show the user the error, and explain the cause in one or two sentences.
2. **Ask the user whether you may fix it.** Do not edit the skill files before they say yes.
3. After the fix, re-run the failing step to confirm it works, and keep it working on Linux too.
4. Then commit in `~/.claude/skills` (small message describing the fix) and push. Ask before pushing if
   unsure the user has write access; if the push is rejected, offer to open a pull request
   (`gh pr create`) or tell them to send the patch to the repo owner. Never force-push.
