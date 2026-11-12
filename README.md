# Claude Code personal skills

Personal skills shared across machines. Clone into `~/.claude/skills`:

    git clone <repo-url> ~/.claude/skills

Then pull to update. `synced/` is managed by claude.ai and is git-ignored.

- `antigravity/` : delegate parallel work to the Antigravity CLI (`agy`), quota-checked.
- `task-progress/` : live terminal progress view (bar, step, log) for long tasks.
- `plan-together/` : show a short plan (steps, skills/agents, risks) and work in small steps with the user.
- `herdr-usage/` : Herdr window showing Claude Code and Antigravity usage limits. Run `herdr-usage/install.sh`, then `herdr-app do mod.open '{"name":"usage"}'` (again closes it). For an always-visible sidebar version, add a block `{"type":"block","size":{"px":275},"content":{"mod":"usage","props":{"compact":true}}}` to a cloned layout.
- `research-kb/` : cite real papers/blog posts, keep a verified knowledge base (`~/.research-kb`); long articles are read by Antigravity's cheap Flash model with quote-checked output. Browse it in Herdr: run `research-kb/install.sh`, then `herdr-app do mod.open '{"name":"knowledge"}'`.

## Maintenance
Skills tell Claude to ask permission, fix any bug it hits (notably on Windows/macOS, where they are untested),
and push the fix here. Requires write access to this repo; otherwise Claude proposes a PR.
