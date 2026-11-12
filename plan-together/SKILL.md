---
name: plan-together
description: Plan with the user before acting and work in small steps. Use at the start of EVERY request that involves doing work (editing or creating files, running commands, git/push, installing, launching agents or delegating, multi-step tasks), and again before each next chunk. The user can switch to autonomous mode ("run on your own", "I'm going to sleep"). Skip only for pure questions or tiny read-only lookups.
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

## Autonomous mode (user opt-in, per task)

The user can lift the step-by-step approval, e.g. "run it on your own", "I'm going to sleep", "just do it".
This is more liberty, not free running:
1. **Ask first, every time.** Never assume it. Confirm in the plan: the one task, the steps you will do, and its limits.
   Wait for a clear yes. A past yes does not carry over to the next task.
2. **Only that task.** Do the agreed steps without asking between them, then stop. Do not start follow-ups, extra
   fixes or new ideas; list them at the end as suggestions.
3. **Limits are agreed in the plan.** Anything hard to undo or outward-facing (push, delete, spending quota or money,
   sending data out, touching other projects) is only done if the user approved that exact action in the plan;
   otherwise skip it and report it. If something unexpected or risky comes up, stop and wait rather than improvise.
4. **Keep it followable.** Use `task-progress` so progress is visible, commit in small steps, and finish with a short
   report: done, skipped, problems, suggested next steps.
5. **It ends with the task.** Back to planning together and small chunks afterwards, unless the user says otherwise.
