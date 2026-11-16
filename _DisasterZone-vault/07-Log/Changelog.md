---
tags: [log]
updated: 2026-11-16
---

# Changelog

Newest first. Addon and tooling changes in this repo; the addon's own player-facing notes stay in its changelog.

## 2026-11-16 - 1.6.0 released, launcher 0.6.0 published

- `release-1.6.0` (Latest): version 1.6.0, What's New with credits to Tsumil, our Discord bot's key for
  `Casual Disaster-Thunderstrike` (PR #9), release record `dev/releases/1.6.0.json` (PR #10).
- `main`: member download page + launcher workflow (PR #11).
- `launcher-v0.6.0` (not Latest): Windows installer from the workflow (signed updater, feed `launcher-latest`) and a
  locally built Linux AppImage (no self-update yet: card `launcher-linux-self-update`).

## 2026-11-16 - Launcher 0.6.0 for TBC (from the 0.5.0 source)

- `launcher/`: the 0.5.0 source members run (src-tauri, ui, proto, package files) replaces the older 0.4.0 copy; the
  bot server (`launcher/server`) stays. Version 0.6.0, same identity (`com.disasterzone.launcher`, "DisasterZone
  Launcher"), so it installs over the old launcher and keeps its settings and Discord link.
- Addon feed off: the launcher refuses the original releases repository as its source (`state::is_upstream_source`,
  `Settings::release_source`) for every game version, so it never installs, updates or auto-installs the old 1.5.5
  addon from it. The hero says "Updates off" and opens the releases page; Discord sync works as before.
- Bot server: `launcher/server.txt` is empty in the repository; the Windows build writes it from the `DZ_BOT_SERVER`
  secret. Sync and presence say "no bot server is set" instead of calling a relative URL.
- Self-update from this repository: new updater public key and the feed
  `releases/download/launcher-latest/latest.json` in `tauri.conf.json`. Releases page link points here.
- From the Forever port: the Discord link survives a restart on Linux (keyring Secret Service), and the game is found
  under Wine/Proton by its command line (`wow::in_folder_wine`).
- About credits the original author (Tsumil) and the maintainer (Arakis).
- `.github/workflows/launcher-windows.yml`: Windows installer + `latest.json` as the artifact `dz-tbc-launcher-windows`
  on pull requests, launcher tags and Run workflow; publishing (release `launcher-v<version>` with `--latest=false`,
  the `launcher-latest` feed) only when run by hand with "publish" on the tag.

## 2026-11-16 - Discord bot key per guild; dev install into the TBC client

- `Core/Bridge.lua`: `Bridge.KeyFor(guildKey)` reads `ns.BridgeKeys[guildKey]` (one bot key per guild, the form the
  bot's keygen writes); the older single `ns.BridgeKey` still works. From the Forever port, with its bridge cases.
- `dev/install_tbc.sh`: copies this checkout into the TBC Anniversary client (`_anniversary_/Interface/AddOns`) as a
  "dev" build (in-game updates skip it): the maintainer's own client runs dev, members run releases. `--all` adds every
  game pack, `--remove` takes the folders out. Saved data is never touched.

## 2026-11-16 - Fixes and features from the Forever port (security, sync, loot, recruitment)

Brought over from the Forever port after checking each against 1.5.5 (the bug present in 1.5.5, or the feature
working on TBC). Forever-only code left out. One commit per item on the PR.

- **Security, relayed records:** the GM's rules travel on their own `GMR` record, taken only from the Guild Master;
  a reserves list (`RVS`) only from the loot authority or its holder; relayed raid plans, sign-ups and team waitlists
  only from their writer, a raid planner, the raid's leader or the Discord host (else held back and asked for); guest
  book, officer notes and recruit records relayed by someone else are marked; LootReserve read only from the leader,
  master looter or loot authority; raid blacklist and ledger awards keep who passed them on; role-gated records
  (events, polls, prized items, strategies) only from someone who could have written them.
- **Security, small holes:** feedback items, me-toos and replies only from their author or staff; the feedback plan
  ("Coming next") only from the developer; a live event's chain vouches for nobody; dungeon runs only from their owner;
  professions only from the member or an officer.
- **Events and polls:** relays held back unless vouched, asked for from a role holder; a recheck (`XXR`) after a
  catch-up so a login wave converges; the guild council list changes only from the GM's own copy.
- **Data and loot:** duplicate drops (each copy uses up one reservation; two copies won by one player are two awards
  in the loot log); event sign-ups survive a catch-up; an open roll comes back after /reload (`RQ`).
- **Sync:** "couldn't take X's BiS list" said once per player per session; my version whispered back to a late
  login (`V`); the roster lists anyone heard with DisasterZone.
- **State-machine audit:** one raid-over cut-off; one sign-up path (a long Discord note is refused, not dropped);
  invite & sort stops when its raid is cancelled or deleted; event handover keeps the host when the state can't go
  out; the demo toggle cancels my open rolls; one award transition; the former reserves host writes only while no
  authority is known.
- **Raids, Discord, Chess:** a Discord answer to a locked raid is a request to join; the guild key takes the guild's
  realm (connected realms); Chess results from the wire are concessions, a ladder draw only from one of the players,
  ladder catch-up only from the one asked.
- **Recruitment:** recruiters share messages and places, a message per place, text markers in channels (Say/Yell keep
  the raid icons), whispers after a post land in Recruitment as Talking.
- **`/dz update`** installs a downloaded update (the interface reloads) or asks the guild at once.
- **Client safety:** every keyboard-propagation call goes through `Util.SetPropagateKeys` (skipped in combat, applied
  after); no global `_` write.
- New suites: `sync/test_authority*.py`, `sync/test_sync_notices.py`, `sync/test_connected_realms.py`,
  `events/test_events_catchup.py`, `keybinds/test_combat_keys.py`, `raidplan/test_raidplan_signup_paths.py`.
  Full run 304 suites, 0 failed.

## 2026-11-16 - The download link, easy to copy

`/dz download` (and `/dz link`) print the download link and open a box with it selected (Ctrl+C, then paste it to
whoever needs DisasterZone); Settings > About has a "Download link" row with a **Copy link** button for the same box.
One address for all of them and the game hub's "Get the game": `Util.DOWNLOAD_URL` (the newest release on this repo's
Releases page). Test: `tests/boot-ui/test_download_link.py`.

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
