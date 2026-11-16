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
luaenv/bin/python tf_e/run_all.py --all -j 8                    # ~5 min, forking on (the default)
DZ_FORK=0 luaenv/bin/python tf_e/run_all.py patch/ --all -j 4   # the patch suites cannot fork
```

- Never set `DZ_NATIVE_CACHE` under `/tmp`: it can grow to several GB in one run.
- ⚠️ **Memory.** Keep forking on (`DZ_FORK=0` only for `patch/`): without it a suite keeps every case in one
  process (`strategy/test_strategy_live` reaches ~5 GB, `votes/test_votes` ~3 GB). `scale/test_raid_night` needs
  ~5 GB per shard even forked, and runs 4 shards side by side. On a 32 GB machine a full run at `-j 12` with
  forking off fills RAM and swap, and the system OOM killer (systemd-oomd) then kills the whole terminal. Run long
  test jobs in their own capped unit, so only the tests die if they run out:
  `systemd-run --user --unit=dz-tests --collect -p MemoryMax=16G -p MemorySwapMax=1G <script>`.

## Baseline on 1.5.5

**2026-11-16: 0 failed.** Forking on, every area but `patch/`: 270 suites, 0 failed. `DZ_FORK=0 --all`: 291 suites,
0 failed. `tools/check.py -q`: 0 syntax errors, 39 style ("uniformity") errors carried from upstream. Any failure is
a regression.

Before the Linux fixes (same day) 5 suites failed, all upstream test bugs: the UI audit loaded Segoe UI from a Windows
path (`events/test_edge_tab`, `test_kinds_ui_qa`), two Azeromon suites depended on the time of day, and
`sync/test_mixed_versions` needed the tag `release-1.4.0` with the addon source in it.

## Not in git

- `dev/luaenv/` and `dev/.slots/` (recreate above)
