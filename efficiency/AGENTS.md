# Keep Claude usage low (applies to every session)

Every turn re-reads the whole conversation, so big reads and long sessions are what burn the quota.
- Read narrowly: `rg`/`grep -n` then read a line range. Never read a whole large file or doc "to be safe"; no `cat` of big outputs (pipe through `head`/`tail`/`rg`).
- Screenshots and images stay in context for the rest of the session: take one only when it answers a question text cannot, and prefer `herdr-app status`/`ls` or logs.
- **Delegate reading to Antigravity (hard rule).** Never read into your own context a file, notebook, web page, paper, log or command output that is over ~150 lines / ~8 KB, unless you must edit it. Instead run Flash on it (quota-checked, quotes re-verified, ~14 s):
  - files, notebooks, remote files, logs: `python3 ~/.claude/skills/antigravity/scripts/agy_read.py PATH|- --ask "question"` (`-` = stdin, e.g. `ssh fir cat f | agy_read.py - --ask ...`)
  - papers, blog posts, docs URLs: `python3 ~/.claude/skills/research-kb/scripts/kb.py read URL --ask "question"`
  - Trust only the ✓ lines. Read a small range yourself only for the lines you will edit or quote. Tests and independent reviews also go to `agy` (skill `antigravity`).
- One session per task or project. Suggest a fresh session when the topic changes or the context is large (past ~100k tokens).
- Skills: do not open SKILL.md files speculatively. `~/.claude/skills/INDEX.md` is a one-screen table of when each skill applies; open only the skill(s) that match the request.
- Use the cheapest thing that works: `grep` before reading, one command with several checks instead of many small calls, short answers.
