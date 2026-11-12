# Keep Claude usage low (applies to every session)

Every turn re-reads the whole conversation, so big reads and long sessions are what burn the quota.
- Read narrowly: `rg`/`grep -n` then read a line range. Never read a whole large file or doc "to be safe"; no `cat` of big outputs (pipe through `head`/`tail`/`rg`).
- Screenshots and images stay in context for the rest of the session: take one only when it answers a question text cannot, and prefer `herdr-app status`/`ls` or logs.
- Bulk reading, long-document summaries, test runs and independent reviews go to Antigravity (skill `antigravity`, cheap Flash model, quota-checked first) instead of being done here.
- One session per task or project. Suggest a fresh session when the topic changes or the context is large (past ~100k tokens).
- Skills: do not open SKILL.md files speculatively. `~/.claude/skills/INDEX.md` is a one-screen table of when each skill applies; open only the skill(s) that match the request.
- Use the cheapest thing that works: `grep` before reading, one command with several checks instead of many small calls, short answers.
