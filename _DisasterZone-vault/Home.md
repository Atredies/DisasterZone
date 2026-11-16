---
tags: [meta]
updated: 2026-11-16
---

# DisasterZone

> The <Casual Disaster> guild addon for **WoW TBC Anniversary** (Interface 20506), continued from release 1.5.5.
> Written by [tsumilo](https://github.com/tsumilo) ([DisasterZone-dev](https://github.com/tsumilo/DisasterZone-dev),
> [DisasterZone-releases](https://github.com/tsumilo/DisasterZone-releases)). These notes cover the addon, its dev
> tooling and its tests.

## Branches

| Branch | Holds |
|---|---|
| `main` | the release tree (signed file lists in `channels/`, files in `objects/`, the launcher), as members get it |
| `dev` | the source: addon, specs, the WoW-mock test harness, release tools, launcher source. Work lands here |
| `upstream-1.6.0` | the original author's unreleased work past 1.5.5, kept for reference |

## Overview

- [[Project Overview]]: what the addon does and where this repo starts from

## Roadmap

- Board: [[Work.base|Work]] (cards in `04-Roadmap/Tasks/`)

## Operations

- [[Linux Dev Setup]]: one-time setup of the Python/Lua test environment, and the test baseline
- Upstream's own docs stay in `dev/docs/` (SPEC.md + addenda, HOTPATCH.md, GAME_PACKS.md, research/api.md) and the
  root `README.md` (layout, everyday commands, making a change, releasing)

## Log

- [[Changelog]] · [[Decision Log]]
