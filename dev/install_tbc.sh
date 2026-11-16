#!/usr/bin/env bash
# Dev install of DisasterZone into the WoW TBC Anniversary client, straight from this checkout (a "dev" build: in-game
# updates never apply to it, and the old launcher leaves a "dev" build alone). Members get the prod releases instead.
# Game packs are optional: name them to include them.
#   dev/install_tbc.sh                          # the main addon + DisasterZone_Rooms (Chess needs it)
#   dev/install_tbc.sh Bingo Chess              # plus DisasterZone_Bingo and DisasterZone_Chess
#   dev/install_tbc.sh --all                    # every DisasterZone_* folder in this checkout
#   dev/install_tbc.sh --remove                 # take every DisasterZone folder out again
# Saved data (WTF/.../SavedVariables/DisasterZone*.lua) is never touched. WOW_DIR overrides the client folder.
# After installing: restart the game if a TOC changed (a new version, a new pack), otherwise /reload.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../addon"
WOW="${WOW_DIR:-$HOME/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft}"
ADDONS="$WOW/_anniversary_/Interface/AddOns"
[ -d "$ADDONS" ] || { echo "No TBC Anniversary AddOns folder at: $ADDONS (set WOW_DIR)"; exit 1; }
if [ "${1:-}" = "--remove" ]; then
    for d in "$ADDONS"/DisasterZone "$ADDONS"/DisasterZone_*; do [ -e "$d" ] && rm -rf "$d" && echo "removed $d"; done
    exit 0
fi
folders=(DisasterZone DisasterZone_Rooms)
if [ "${1:-}" = "--all" ]; then
    for d in "$SRC"/DisasterZone_*; do b=$(basename "$d"); [ "$b" = DisasterZone_Rooms ] || folders+=("$b"); done
else
    for p in "$@"; do folders+=("DisasterZone_$p"); done
fi
for f in "${folders[@]}"; do
    [ -d "$SRC/$f" ] || { echo "no such addon folder: $SRC/$f"; exit 1; }
    rsync -a --delete --exclude '.claude' "$SRC/$f/" "$ADDONS/$f/"
    echo "installed $ADDONS/$f"
done
# (Core/DevPlan.lua is git-ignored and listed in the TOC: an empty one keeps the client from a missing-file error)
[ -f "$ADDONS/DisasterZone/Core/DevPlan.lua" ] || : > "$ADDONS/DisasterZone/Core/DevPlan.lua"
grep -m1 '^## Version' "$ADDONS/DisasterZone/DisasterZone.toc" | tr -d '\r'
grep -m1 'id = ' "$ADDONS/DisasterZone/Core/BuildInfo.lua" | tr -d '\r' || true
