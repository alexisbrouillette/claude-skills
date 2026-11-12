#!/usr/bin/env bash
# Resolve the Antigravity CLI on any machine, then pass all args through.
# Usage: agy.sh quota | agy.sh models | agy.sh run <model> <prompt...> | agy.sh <raw agy args>
set -euo pipefail
AGY="$(command -v agy || true)"
for p in "$HOME/.gemini/bin/agy" "$HOME/.local/bin/agy" "/usr/local/bin/agy"; do
  [ -z "$AGY" ] && [ -x "$p" ] && AGY="$p"
done
[ -z "$AGY" ] && { echo "agy not found. Install Antigravity CLI and sign in first." >&2; exit 127; }
cd "${AGY_CWD:-$PWD}"
# Session-only, never saved. Narrow READ-ONLY allow-list for headless runs (no prompting possible).
# Anything not listed is auto-denied: the failure then surfaces to Claude, who asks the user when unsure.
# Each * matches ONE token, so rules are generated for 0-6 argument tokens.
# Deliberately excluded: cat/cp/mv/rm/curl/sh/npm/git push|checkout|commit (can read secrets or change state).
SAFE_SETTINGS='{"permissions":{"allow":["command(git diff)","command(git diff *)","command(git diff * *)","command(git diff * * *)","command(git diff * * * *)","command(git diff * * * * *)","command(git diff * * * * * *)","command(git log)","command(git log *)","command(git log * *)","command(git log * * *)","command(git log * * * *)","command(git log * * * * *)","command(git log * * * * * *)","command(git show)","command(git show *)","command(git show * *)","command(git show * * *)","command(git show * * * *)","command(git show * * * * *)","command(git show * * * * * *)","command(git status)","command(git status *)","command(git status * *)","command(git status * * *)","command(git status * * * *)","command(git status * * * * *)","command(git status * * * * * *)","command(rg)","command(rg *)","command(rg * *)","command(rg * * *)","command(rg * * * *)","command(rg * * * * *)","command(rg * * * * * *)","command(grep)","command(grep *)","command(grep * *)","command(grep * * *)","command(grep * * * *)","command(grep * * * * *)","command(grep * * * * * *)","command(ls)","command(ls *)","command(ls * *)","command(ls * * *)","command(ls * * * *)","command(ls * * * * *)","command(ls * * * * * *)","command(head)","command(head *)","command(head * *)","command(head * * *)","command(head * * * *)","command(head * * * * *)","command(head * * * * * *)","command(tail)","command(tail *)","command(tail * *)","command(tail * * *)","command(tail * * * *)","command(tail * * * * *)","command(tail * * * * * *)","command(wc)","command(wc *)","command(wc * *)","command(wc * * *)","command(wc * * * *)","command(wc * * * * *)","command(wc * * * * * *)"]}}'
case "${1:-}" in
  quota)  shift; exec timeout 60 "$AGY" -p "/usage" ;;
  models) shift; exec timeout 60 "$AGY" models ;;
  run)    shift; model="$1"; shift
          exec "$AGY" -p "$*" --model "$model" --mode "${AGY_MODE:-plan}" --settings "$SAFE_SETTINGS" ;;
  watch)  shift; export AGY_SETTINGS="$SAFE_SETTINGS"; exec python3 "$(dirname "$0")/agy_watch.py" "$@" ;;
  *)      exec "$AGY" "$@" ;;
esac
