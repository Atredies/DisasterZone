---
title: "Bring the Forever fixes and features to TBC"
tags: [task]
status: 1 - In progress
priority: p2
effort: L
updated: 2026-11-16
---

# Bring the Forever fixes and features to TBC

From the Forever repo's changelog (0.2.6 to 0.2.8), the ones that apply to TBC:

- [x] Raid times: one Local / Server clock switch (`settings.serverClock`)
- [x] A busy calendar day turns in pages instead of "+N more"
- [x] Bingo: view another raider's card from the race
- [x] Guild key from the guild's realm (connected realms share the guild's data)
- [x] A Discord answer to a locked raid becomes a request to join
- [x] Chess ladder catch-up only from the one asked
- [x] Whisper buttons through the game's SendTell
- [x] Recruitment: whispers after a post join Recruitment; recruiters share messages and places; one message per place
- ~~Guild invite through a secure `/ginvite` button~~: not for TBC (its GuildInvite works from a click; owner, 2026-11-16)

Forever was forked from the 1.6.0 trunk, so check each change against 1.5.5 (`dev`) and leave out Forever-only code.

## Done when

Each item is on `dev` (or marked "not for TBC" with why), the baseline is green, and a release carries them.

## 2026-11-16

Ported with the security, sync, loot and audit fixes (see the Changelog). Left: release them in 1.6.0.
