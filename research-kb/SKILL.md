---
name: research-kb
description: Ground research and technical-design work in real papers and blog posts, cite them, and keep a verified knowledge base the user can browse in Herdr. Use whenever work depends on factual claims from the literature (methods, benchmarks, algorithm choices, "what does the research say", model/library behaviour), when the user asks for sources, or when starting research/development on a new topic. Not for routine coding.
---

# Research knowledge base

Goal: no unsupported claims. Every non-obvious factual claim comes from a source we can show, and every source
we rely on goes into the KB with a one-line "why it helped us". The user reads the KB in Herdr (mod `knowledge`).

Script: `KB="python3 ~/.claude/skills/research-kb/scripts/kb.py"`. Store: `~/.research-kb/entries.jsonl` (global).
All commands print short output on purpose. Never paste whole articles into the conversation.

## Workflow

1. **Search the KB first** (free): `$KB search "topic words"`. Reuse what is there; do not re-research it.
2. **Find sources** if missing: `$KB find "query" -n 4` (arXiv + Crossref: title, authors, year, URL, short abstract).
   For blog posts or docs, use URLs the user gives or that you already know exist; there is no search engine here, so
   say so rather than guessing a URL. Never write a citation from memory without verifying it.
3. **Read through the cheap model, always**: `$KB read <url> [--ask "specific question"]`.
   Antigravity's Flash model reads the full article (HTML or PDF) and returns a summary plus claims with verbatim
   quotes that the script re-checks against the text. This keeps long articles out of your context.
   - Do NOT fetch and read articles yourself with curl/Read. Use `read`.
   - Only claims marked ✓ are confirmed. The SUMMARY is model-written: do not repeat it as fact, use the ✓ claims.
   - Exit code 3 = Antigravity quota low: tell the user, do not work around it (reading it yourself is the user's call).
   - Use `--ask` to focus the extraction on what we actually need; it is cheaper and better.
4. **Save what you use**: `$KB add <url> --why "<one line: what it told us / why it mattered for THIS work>" [--project P] [--tags a,b]`.
   `add` verifies the source exists (arXiv API, Crossref, or the page) and takes title/authors/year from the source,
   never from you. `REFUSED` means it could not be verified: do not cite it, and do not retry with `--unverified`
   unless the user agrees. Write `--why` in plain language about our project, not an abstract of the paper.
5. **Cite in your answer**: name the source (Author year, title) and give the URL next to each claim it supports.
   A claim you cannot back: say "unverified" or "my inference". Do not dress guesses as findings.

## Token discipline
- Look things up only when a claim matters to a decision. Skip it for common knowledge and routine coding.
- Prefer 2-4 strong sources over many weak ones. Search the KB before the web.
- One `read` per source; use `--ask`. Do not re-read a source already in the KB unless the question is new.

## Honesty rules
- Quotes and numbers come from `read` output (✓ lines) or the user, not from memory.
- If the source disagrees with what you expected, say so; do not bend it.
- Privacy: only public articles go through `read` (their text is sent to Google via Antigravity). Never pass private
  documents, secrets, or unpublished work to it.

## Maintenance
`$KB list -n 10` shows the newest entries; `$KB rm <id>` removes one (ask the user first).
If the script breaks, follow the same rule as the other skills here: show the error, ask before editing the skill, then fix and push.
