#!/usr/bin/env bash
# Install the Knowledge base mod into the Herdr app (re-run after `git pull`).
set -euo pipefail
dst="${HERDR_APP_HOME:-$HOME/.config/herdr-app}/mods/knowledge"
mkdir -p "$dst"; cp "$(dirname "$0")"/herdr/* "$dst"/
herdr-app check "$dst"
echo "Installed. Open/close it with: herdr-app do mod.open '{\"name\":\"knowledge\"}'"
