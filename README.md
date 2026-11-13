# Claude Code personal skills

Personal skills shared across machines. Tested on Linux only.

## Setup from scratch

1. **pi** (the agent; needs Node 22.19+, the installer offers to install it):
   `curl -fsSL https://pi.dev/install.sh | sh`, then run `pi` once and sign in to a model provider
   (`pi --no-browser` gives a device-code sign-in for SSH sessions).
2. **Herdr** (`herdr-app` and `hc`, the panes and remote machines): install it from wherever you got it
   (TODO: add the download link here). Check with `hc --version` and `herdr-app --version`.
3. **Skills** (needs read access to this repo):

       git clone https://github.com/alexisbrouillette/claude-skills ~/.claude/skills
       mkdir -p ~/.pi/agent && ln -sf ~/.claude/skills/efficiency/AGENTS.md ~/.pi/agent/AGENTS.md

   Pull to update. `synced/` is managed by claude.ai and is git-ignored.
4. **Optional tools**, only for the skills that use them:

   | Skill / feature | Needs |
   |---|---|
   | `antigravity` | the `agy` CLI, signed in (run `agy` once interactively) |
   | `pr-review` | `gh` logged in (`gh auth login`), `git`, a browser (`xdg-open`) |
   | `herdr-usage`, `research-kb` panes | run each skill's `install.sh` |
   | Remote machines and Slurm cards | `hc machine add user@host` (a person types the login/MFA once) |
   | `task-progress` in Herdr | nothing: the pane installs itself the first time a task opens it |

5. **Check**: start `pi` and ask "which skills do you have?". Try `python3 ~/.claude/skills/task-progress/scripts/progress.py demo`.

- `antigravity/` : delegate parallel work to the Antigravity CLI (`agy`), quota-checked. Headless runs use a session-only read-only command allow-list (anything else is denied and I ask you). `agy.sh watch` shows live steps in the shared progress pane.
- `pr-review/` : review a PR; the diff review goes to `agy`, visual PRs are opened on the local server in your browser with a "what to verify" checklist.
- `task-progress/` : one shared Herdr pane with a card per task (step line, log; a bar only when a real percentage exists). `scripts/slurm_watch.py` shows Slurm jobs of a remote machine (reads tqdm progress from job logs); `scripts/hc_watch.py` shows any `hc` terminal. Plain terminal fallback outside Herdr.
- `plan-together/` : show a short plan (steps, skills/agents, risks) and work in small steps with the user.
- `herdr-usage/` : Herdr window showing Claude Code and Antigravity usage limits. Run `herdr-usage/install.sh`, then `herdr-app do mod.open '{"name":"usage"}'` (again closes it). For an always-visible sidebar version, add a block `{"type":"block","size":{"px":275},"content":{"mod":"usage","props":{"compact":true}}}` to a cloned layout.
- `research-kb/` : cite real papers/blog posts, keep a verified knowledge base (`~/.research-kb`); long articles are read by Antigravity's cheap Flash model with quote-checked output. Browse it in Herdr: run `research-kb/install.sh`, then `herdr-app do mod.open '{"name":"knowledge"}'`.
- `research-kb/herdr-button/` : sidebar button (with source count) that opens the Knowledge base window; add a block `{"id":"kb-button","type":"block","size":{"px":34},"content":{"mod":"kb-button"}}` to a cloned layout.
- `antigravity/scripts/agy_read.py` : have the cheap Flash model read big files/logs/notebooks (quote-checked) instead of Claude.
- `INDEX.md` : one-screen table of when to use which skill.
- `efficiency/AGENTS.md` : always-on rules to keep usage low. Link it: `ln -sf ~/.claude/skills/efficiency/AGENTS.md ~/.pi/agent/AGENTS.md`.

## Maintenance
Skills tell Claude to ask permission, fix any bug it hits (notably on Windows/macOS, where they are untested),
and push the fix here. Requires write access to this repo; otherwise Claude proposes a PR.
