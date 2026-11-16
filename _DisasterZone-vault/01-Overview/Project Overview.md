---
tags: [overview]
updated: 2026-11-16
---

# Project Overview

**What:** DisasterZone, the guild addon of <Casual Disaster> on TBC Anniversary: loot council, soft reserves, raid
plans and sign-ups, attendance, BiS lists, roles, polls, recruitment, strategy boards, boss mods, Atlas and the
guild games (Rooms, Bingo, Azeromon, Hold the Line, Chess, Illidan, Trainer). The repo also holds a Rust desktop
launcher and a Discord bot server (`launcher/`).

**Where it starts:** release **1.5.5** (stable, seq 13), the version the guild runs. `dev` is the source at commit
`3ccb5a72` ("1.5.5: version and changelog date"), the commit that release was built from (`channels/stable.json`
on `main`). The original author's later, unreleased work (57 commits, the 1.6.0 notes) is on `upstream-1.6.0`.

**What comes next:** the fixes and features built since in the WoW Forever port
([Atredies/DisasterZoneForever](https://github.com/Atredies/DisasterZoneForever)), brought to TBC one by one. Forever
was forked from the 1.6.0 trunk (`e21d5a9c`), not 1.5.5, so a Forever change can touch code that only exists in
1.6.0: check each against 1.5.5 before applying it. Forever-only code (`ns.Compat.isForever`, the level-60 cap,
Forever raids, "First Last" names) does not come over.

**Releases:** signed. Members' existing copies only accept updates signed with the original author's keys, so the
first release from this repo is a full download for everyone; saved data (SavedVariables) is kept, because the addon
folder and variable names stay the same.
