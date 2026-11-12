---
name: pr-review
description: Review a PR; when the diff has visual elements (UI, CSS, templates, components, assets), run it on the local server, open the affected page in the user's browser, and say exactly what to verify. Use when the user says we are reviewing a PR.
---

# PR review

## 0. Delegate the reading (always)
Load the `antigravity` skill and send the diff review to `agy` (quota-checked first), especially for long PRs. Give it the PR number and the checklist in section 1; ask for findings by severity with file:line, and for the list of visual files/routes. Do not read the full diff here; only open the specific lines it flags. If agy is unavailable or quota is low, tell the user and fall back to narrow reads.
Local steps (checkout, server, browser) stay here.

## 1. Standard checks (always; done by agy)
- `gh pr view` + `gh pr diff` (description, files, CI status). Use `rg`/line ranges, not whole files.
- Diff matches the description; correctness and edge cases.
- Tests added/updated; run result. Big test runs go to Antigravity.
- Lint, types, CI green.
- Security (secrets, injection, risky deps), breaking changes, migrations.

## 2. Visual detection
Visual if the diff touches components, styles (css/scss/tailwind), templates/html, images/icons/fonts, or layout/routing for pages.
If not visual, skip to the report.

## 3. Visual PRs: open locally
Ask once before state changes (checkout, starting server).
1. `gh pr checkout <n>`.
2. Detect the dev command (`package.json` scripts, README, Makefile); reuse a server already running on its port.
3. Run it in the background, wait until it responds (`curl -s -o /dev/null`).
4. Work out the affected route(s) from the diff and open each: `xdg-open http://localhost:<port>/<route>`.

## 4. Tell the user what to verify
For each opened page give a short checklist:
- What changed and where to look on the page.
- States to trigger: hover/focus, empty, loading, error, long text.
- Viewports: mobile and desktop width.
- Dark mode, if the app has it.
- Neighbouring elements/pages that might regress.
- Console errors and broken network requests.
Be specific (element names, expected look), not generic.

## 5. Report
Short: findings by severity, then the visual checklist. No screenshots unless text cannot answer.
