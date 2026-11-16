---
tags: [log]
updated: 2026-11-16
---

# Changelog

Newest first. Addon and tooling changes in this repo; the addon's own player-facing notes stay in its changelog.

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
