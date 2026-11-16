---
tags: [log]
updated: 2026-11-16
---

# Changelog

Newest first. Addon and tooling changes in this repo; the addon's own player-facing notes stay in its changelog.

## 2026-11-16 - Developer key, credits, own update key, upgrade check

- **Developer = Arakis-Thunderstrike** by name and realm (`Util.DEV_KEY`, `Util.IsDevKey`): the feedback inbox and
  badge, staff replies, the Performance page, the boss-learning review and `/dz role`. Before, any character named
  Tsumil on any realm counted. Feedback sent to the previous developer carries over.
- **Credits:** Settings > About ("Created by Tsumil (tsumilo on GitHub). Maintained by Arakis since 1.6.0."), every
  TOC's `## Author`. The in-game download link points at this repo's Releases.
- **Own in-game update key** (`Core/PatchKey.lua`, root `9b1288d4`, 1024 one-time signatures). The original author's
  update and bot keys are refused in game (`Patch.IsUntrustedKey`, `Core/Bridge.lua`) and by `release.py`; their
  private halves are lost. Test: `tests/patch/test_untrusted_keys.py`.
- **`dev/tools/upgrade_check.py`**: loads a real saved-variables file from an older release into this build and
  compares every saved variable's entry counts before and after. On a real 1.5.5 file: nothing lost that 1.5.5 itself
  keeps (one strategy assignment for a past raid is pruned by both).

## 2026-11-16 - Raid times in server or local time, busy calendar days in pages, other raiders' Bingo cards

Brought over from the Forever port (its 0.2.6). One **Local / Server** switch (Settings > Window, and on the Home
calendar and Raids tab; `settings.serverClock`, off = local) for every raid screen: Home calendar, Raids tab, raid
plan, raid sheet, attendance and notifications. A busy calendar day shows its raids in pages (`< 1/2 >`, mouse wheel)
instead of an unclickable "+N more". Council Bingo: click a raider in the race to see their card (worked out from the
game's seed, no new message); "My card" goes back. `dev/tools/run_capped.sh`: the full test run in a capped unit
([[Linux Dev Setup]]). Full run 291 suites, 0 failed.

## 2026-11-16 - Tests green on Linux

Brought over from the Forever repo: the UI audit falls back to Liberation Sans / Noto Sans when Segoe UI is missing
(`dev/tools/ui_audit.py`, or pick one with `DZ_PROXY_FONT`), and the Azeromon craft / fix-side suites pin the game
clock to noon. `sync/test_mixed_versions` takes `release-1.4.0` only when that tag holds the addon source (this repo
also carries the release tree's tags, whose `release-1.4.0` has none), else the Release 1.4.0 commit `1209b80d`.
Baseline now 0 failed; how to run it without running out of memory: [[Linux Dev Setup]].

## 2026-11-16 - Repo set up from release 1.5.5

`main` = the 1.5.5 release tree, `dev` = the 1.5.5 source (`3ccb5a72`), `upstream-1.6.0` = the original author's
unreleased work. Releases `release-1.5.5` and `launcher-v0.5.0` copied from the original repo. README credits,
`.gitignore` for Linux test caches, this vault. Test baseline in [[Linux Dev Setup]].
