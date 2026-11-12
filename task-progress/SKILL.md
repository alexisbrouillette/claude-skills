---
name: task-progress
description: Live progress pane (Herdr) or terminal window for tasks over ~30 s: builds, tests, installs, migrations, long delegations. Also when the user asks to see progress.
---

# Task progress viewer

The user cannot easily follow progress while waiting. For any long task, open a live viewer
in its own terminal and keep it updated. Script: `~/.claude/skills/task-progress/scripts/progress.py`
(stdlib Python 3, no install). Below, `PP="python3 ~/.claude/skills/task-progress/scripts/progress.py"`.

## Workflow

1. **Init** a state file in the scratchpad (not the project): `$PP init "$F" --title "Short name" --desc "One line on what and why"`
   (`F=<scratchpad>/progress-<task>.json`).
2. **Open the viewer**: `$PP open "$F"`. All tasks share ONE pane (one card per task; finished cards disappear after ~2 min); `open` only creates the pane if it does not exist.
   - Inside **Herdr** (`HC_TERMINAL_ID` set) it installs the bundled `herdr/` mod into `~/.config/herdr-app/mods/task-progress`
     and opens it as a pane under your own, keeping focus on you. `TASK_PROGRESS_SPLIT=right` splits beside instead.
     The user can close it with its × button; the task is unaffected.
   - Elsewhere (or with `--window`) it launches a new terminal window: gnome-terminal, kitty, alacritty, konsole or xterm.
   If it prints that no GUI terminal was found, give the user the printed `watch` command to paste in their terminal (e.g. the VS Code one).
3. **Update at every milestone**, cheaply and often (each call is instant):
   `$PP set "$F" --percent 40 --step "What is happening right now" --log "Notable event"`
   - `--percent` only when you genuinely know it (steps done / total, files processed / total). Omit it when unknown: no bar is shown, only the text step.
     Never invent numbers. Update `--step` even when percent is unknown.
   - `--step` = present-tense plain language ("Running tests: 3 of 8 suites"). `--log` = short past-tense events.
4. **Finish**: `$PP done "$F" --msg "Result in one line"` or `$PP fail "$F" --msg "What went wrong"`. Always call one of them, even on error.
   The viewer stays open until the user presses Ctrl-C.

For a shell command running in the background, wrap the steps around it: init, open, start it with
`run_in_background`, and update from its output while polling (use Monitor / periodic reads, not sleep loops).
If the task has natural phases, split percent ranges across them (e.g. 0-25, 25-60, ...).

## Slurm jobs on a remote machine
`nohup python3 ~/.claude/skills/task-progress/scripts/slurm_watch.py --on fir --every 30 > /tmp/slurm_watch.log 2>&1 &`
One card per job in the shared pane (state, elapsed of time limit, node, last log line). The bar appears only when the job log has a
tqdm bar (`Ep 2/15: 40%|`), otherwise text only. Finished jobs turn into a done/failed card. One instance per machine (pid in /tmp);
stop it with `pkill -f slurm_watch.py`. Each poll runs one `hc run --on <machine>` call (a short terminal there).

## Any hc terminal (e.g. a long command on Fir)
`nohup python3 ~/.claude/skills/task-progress/scripts/hc_watch.py fir/t18 --on fir --title "Short name" --probe '<remote snippet printing one status line>' > /tmp/hc_watch.log 2>&1 &`
One card per `hc` terminal: running time plus the probe line; the card finishes when the terminal exits (exit 0 = done, else failed).
No bar unless the probe line has `NN%`. Do not stop watchers with `pkill -f <pattern>` from a command that contains that pattern (it kills itself); use pids.

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
