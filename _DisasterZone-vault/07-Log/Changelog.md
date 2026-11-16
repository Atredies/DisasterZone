---
tags: [log]
updated: 2026-11-16
---

# Changelog

Newest first. Addon and tooling changes in this repo; the addon's own player-facing notes stay in its changelog.

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
