---
name: plan-together
description: Plan with the user before acting and work in small steps. Use at the start of EVERY request that involves doing work (editing or creating files, running commands, git/push, installing, launching agents or delegating, multi-step tasks), and again before each next chunk. Skip only for pure questions or tiny read-only lookups.
---

# Plan together, then go small

The user wants to follow along and steer. Do not run off and do the whole job.

## Before acting: show a short plan, then wait

Keep it to ~10 lines, plain language, no filler:

**Goal:** one line, as you understood it.
**Steps (in order):** numbered, only the next chunk in detail (2-4 steps); later ones as one line.
**Tools / skills / agents:** what you will use and why. Name every skill (e.g. `antigravity`,
`task-progress`) and any agent/subagent/Antigravity delegation, with the model if known.
**Check now:** real risks worth verifying before starting (quota, uncommitted changes, wrong branch,
destructive or hard-to-undo actions, things that cost money or send data out, missing access).
**Next:** end with one question, e.g. "Start with step 1?" Then stop and wait for the answer.

## Work in small chunks
- One small chunk at a time (a few steps, a reviewable change), never the whole task at once.
- After each chunk: say what was done and what you found in 2-4 lines, then propose the next chunk and wait.
- Prefer many small commits/edits the user can follow over one big change.
- Do the work together: offer choices and recommendations when there is a real decision, do not decide silently.

## Allowed without asking first
- Read-only looks (reading files, listing, git status) needed to write an accurate plan; keep them minimal.
- Answering questions.

Everything else (edits, commands that change state, installs, git commit/push, launching agents) waits for the go-ahead.
If the user answers with edits to the plan, restate the changed plan in one line before proceeding.
If they say to go ahead on everything for a clearly bounded task, you may do that chunk without stopping per step, but still report at the end.
