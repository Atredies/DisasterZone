#!/bin/sh
# Full test run on Linux inside its own systemd unit with a memory cap, so running out of memory kills only the
# tests, never the terminal (systemd-oomd kills a whole terminal scope). See _DisasterZone-vault/06-Operations/Linux
# Dev Setup.md.
#   dev/tools/run_capped.sh            start it (returns at once); results in dev/tf_e/run_{main,patch,scale}.log
#   dev/tools/run_capped.sh --wait     start it and wait, then print the summary
# Watch: systemctl --user status dz-tests
set -e
DEV=$(cd "$(dirname "$0")/.." && pwd)
if [ "$1" = "--inner" ]; then
    cd "$DEV"
    export DISASTERZONE_ADDON_DIR="$DEV/../addon/DisasterZone" DZ_SLOT_DIR="$DEV/.slots"
    luaenv/bin/python tools/check.py -q > tf_e/run_check.log 2>&1 || true
    # run_all.py's first argument is the output folder; the rest are path filters. Every area but patch/ and
    # scale/ forked at -j 8; patch/ cannot fork; scale/test_raid_night needs ~5 GB per shard, so -j 2.
    AREAS=$(cd tests && ls -d */ | grep -vE '^(patch|scale)/' | sed 's|^|tests/|')
    luaenv/bin/python tf_e/run_all.py run_main $AREAS --all -j 8 > tf_e/run_main.log 2>&1 || true
    DZ_FORK=0 luaenv/bin/python tf_e/run_all.py run_patch tests/patch/ --all -j 4 > tf_e/run_patch.log 2>&1 || true
    luaenv/bin/python tf_e/run_all.py run_scale tests/scale/ --all -j 2 > tf_e/run_scale.log 2>&1 || true
    exit 0
fi
systemctl --user reset-failed dz-tests 2>/dev/null || true
rm -f "$DEV"/tf_e/run_main.log "$DEV"/tf_e/run_patch.log "$DEV"/tf_e/run_scale.log
systemd-run --user --unit=dz-tests -p MemoryMax=16G -p MemorySwapMax=1G "$DEV/tools/run_capped.sh" --inner
if [ "$1" = "--wait" ]; then
    while systemctl --user is-active -q dz-tests; do sleep 5; done
    systemctl --user show dz-tests -p Result --value 2>/dev/null | grep -v '^success$' | sed 's/^/UNIT RESULT: /' || true
    tail -1 "$DEV/tf_e/run_check.log"
    grep -hE "^== |FAILED|^      FAIL" "$DEV/tf_e/run_main.log" "$DEV/tf_e/run_patch.log" "$DEV/tf_e/run_scale.log"
fi
