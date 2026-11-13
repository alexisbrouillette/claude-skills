# Skills: when to open which

Open a skill's SKILL.md only when its row matches the request. (SKILL.md sizes are what loading costs.)

| Skill | Use when | Skip when | Load cost |
|---|---|---|---|
| `plan-together` | About to edit files, run state-changing commands, install, push, delegate, or do multi-step work | Pure questions, tiny read-only lookups | ~600 words |
| `antigravity` | **Reading anything big** (`agy_read.py`: files, notebooks, logs, remote output) is the default, not an exception. Also: user says delegate/second opinion/agy, or bulk reading, tests, review, or independent modules can run in parallel (also to save Claude quota) | Small or sequential tasks, work needing this conversation's context, private/secret data | ~800 words |
| `task-progress` | A task will take more than ~30 s or runs in the background (builds, test suites, installs, long delegations) | Quick commands | ~600 words |
| `pr-review` | User says we are reviewing a PR; review is delegated to agy; visual diffs get opened locally in the browser with a verify checklist | Non-PR work | ~450 words |
| `research-kb` | Work depends on claims from papers/blog posts, the user wants sources, or a new research topic starts | Routine coding, common knowledge | ~600 words |

Always-on rules live in `efficiency/AGENTS.md` (linked as `~/.pi/agent/AGENTS.md`), not in a skill.
