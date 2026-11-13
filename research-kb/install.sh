#!/usr/bin/env bash
# Install the Knowledge base mod into the Herdr app (re-run after `git pull`).
set -euo pipefail
dst="${HERDR_APP_HOME:-$HOME/.config/herdr-app}/mods/knowledge"
mkdir -p "$dst"; cp "$(dirname "$0")"/herdr/* "$dst"/
herdr-app check "$dst"
btn="${HERDR_APP_HOME:-$HOME/.config/herdr-app}/mods/kb-button"
mkdir -p "$btn"; cp "$(dirname "$0")"/herdr-button/* "$btn"/
herdr-app check "$btn"
echo "Installed. Open/close it with (or add a block with mod kb-button to your layout for a sidebar button): herdr-app do mod.open '{\"name\":\"knowledge\"}'"
