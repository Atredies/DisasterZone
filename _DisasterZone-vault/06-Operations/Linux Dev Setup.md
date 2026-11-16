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
tools/run_capped.sh --wait                                      # the full run, ~7 min (below)
```

- Never set `DZ_NATIVE_CACHE` under `/tmp`: it can grow to several GB in one run.
- ⚠️ **Memory.** Keep forking on (`DZ_FORK=0` only for `patch/`): without it a suite keeps every case in one
  process (`strategy/test_strategy_live` reaches ~5 GB, `votes/test_votes` ~3 GB). `scale/test_raid_night` needs
  ~5 GB per shard even forked, and runs 4 shards side by side. On a 32 GB machine a full run at `-j 12` with
  forking off fills RAM and swap, and the system OOM killer (systemd-oomd) then kills the whole terminal. Run long
  test jobs in their own capped unit, so only the tests die if they run out:
  `systemd-run --user --unit=dz-tests --collect -p MemoryMax=16G -p MemorySwapMax=1G <script>`.

## The full run: `dev/tools/run_capped.sh`

Runs `tools/check.py` and every suite in three passes inside its own systemd unit (`dz-tests`, capped at 16 GB), so
running out of memory kills only the tests: every area but `patch/` and `scale/` forked at `-j 8`, `patch/` with
`DZ_FORK=0` (it cannot fork), `scale/` at `-j 2` (~5 GB per shard). Results: `tf_e/run_check.log`,
`tf_e/run_main.log`, `run_patch.log`, `run_scale.log`. Watch with `systemctl --user status dz-tests`.

`run_all.py`'s **first argument is the output folder**, the rest are path filters: `run_all.py patch/ --all` runs
everything into `tf_e/patch/`; filter with `run_all.py myrun tests/patch/ --all`. It has no `--help` (an unknown
first argument is just an output folder name, and the run starts).

## Baseline on 1.5.5

**2026-11-16: 0 failed.** Forking on, every area but `patch/`: 270 suites, 0 failed. `DZ_FORK=0 --all`: 291 suites,
0 failed. `tools/check.py -q`: 0 syntax errors, 39 style ("uniformity") errors carried from upstream. Any failure is
a regression.

Before the Linux fixes (same day) 5 suites failed, all upstream test bugs: the UI audit loaded Segoe UI from a Windows
path (`events/test_edge_tab`, `test_kinds_ui_qa`), two Azeromon suites depended on the time of day, and
`sync/test_mixed_versions` needed the tag `release-1.4.0` with the addon source in it.

## Run the dev build in the game

`dev/install_tbc.sh --all` copies this checkout into the TBC Anniversary client (Wine install under
`~/Games/battlenet`; `WOW_DIR` overrides it). Restart the game when a TOC changed, else `/reload`.

## Not in git

- `dev/luaenv/` and `dev/.slots/` (recreate above)
