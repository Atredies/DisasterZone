---
tags: [operations]
updated: 2026-11-16
---

# Linux Dev Setup

Upstream assumes Windows; these steps need no source edits. Verified 2026-11-16 on Arch Linux, Python 3.14, branch
`dev` (1.5.5). Same as the Forever repo's setup.

```bash
git checkout dev && cd dev
python3 -m venv luaenv
luaenv/bin/pip install -r requirements.txt
luaenv/bin/pip install numpy==2.5.3 pillow==12.3.0 shapely==2.1.2   # some suites need these
mkdir -p luaenv/Scripts && ln -s ../bin/python luaenv/Scripts/python.exe   # run_all hard-codes this path
export DISASTERZONE_ADDON_DIR=$PWD/../addon/DisasterZone           # default is C:\World of Warcraft\...
export DZ_SLOT_DIR=$PWD/.slots
luaenv/bin/python tools/test_harness_selftest.py                 # 13/13
luaenv/bin/python tools/check.py -q
DZ_FORK=0 luaenv/bin/python tf_e/run_all.py --all -j 12          # ~6 min; the patch suites cannot fork
```

- Never set `DZ_NATIVE_CACHE` under `/tmp`: it can grow to several GB in one run.

## Baseline on 1.5.5 (2026-11-16)

`DZ_FORK=0 run_all --all` = **291 suites, 5 failed**, all upstream test bugs, none in the addon:

| Suite | Why it fails |
|---|---|
| `events/test_edge_tab`, `events/test_kinds_ui_qa` | the UI audit loads Segoe UI from a Windows path |
| `games/test_azeromon_craft`, `games/test_azeromon_fix_side` | Azeromon tests pinned to a time of day |
| `sync/test_mixed_versions` (3 cases) | needs the private tag `release-1.4.0` |

Without `DZ_FORK=0` the `patch/` suites fail as well (they cannot run forked). `tools/check.py -q`: 0 syntax errors,
39 style ("uniformity") errors carried from upstream. Anything beyond this list is a regression.

## Not in git

- `dev/luaenv/` and `dev/.slots/` (recreate above)
