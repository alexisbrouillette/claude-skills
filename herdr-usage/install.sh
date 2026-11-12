#!/usr/bin/env bash
# Install the Usage mod into the Herdr app (re-run after `git pull` to update).
set -euo pipefail
dst="${HERDR_APP_HOME:-$HOME/.config/herdr-app}/mods/usage"
mkdir -p "$dst"; cp "$(dirname "$0")"/usage/* "$dst"/
herdr-app check "$dst"
echo "Installed. Open/close it with: herdr-app do mod.open '{\"name\":\"usage\"}'"
