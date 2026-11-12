# Claude Code personal skills

Personal skills shared across machines. Clone into `~/.claude/skills`:

    git clone <repo-url> ~/.claude/skills

Then pull to update. `synced/` is managed by claude.ai and is git-ignored.

- `antigravity/` : delegate parallel work to the Antigravity CLI (`agy`), quota-checked.
- `task-progress/` : live terminal progress view (bar, step, log) for long tasks.
- `plan-together/` : show a short plan (steps, skills/agents, risks) and work in small steps with the user.

## Maintenance
Skills tell Claude to ask permission, fix any bug it hits (notably on Windows/macOS, where they are untested),
and push the fix here. Requires write access to this repo; otherwise Claude proposes a PR.
