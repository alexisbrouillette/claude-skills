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
case "${1:-}" in
  quota)  shift; exec timeout 60 "$AGY" -p "/usage" ;;
  models) shift; exec timeout 60 "$AGY" models ;;
  run)    shift; model="$1"; shift
          exec "$AGY" -p "$*" --model "$model" --mode "${AGY_MODE:-plan}" ;;
  *)      exec "$AGY" "$@" ;;
esac
