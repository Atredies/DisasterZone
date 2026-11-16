---
title: "Launcher: Linux AppImage with self-update"
tags: [task]
status: 4 - Later
priority: p3
effort: S
updated: 2026-11-16
---

# Launcher: Linux AppImage with self-update

Launcher 0.6.0's Linux AppImage was built locally and attached to `launcher-v0.6.0` by hand: it has no updater
signature, and `latest.json` lists only Windows, so a Linux launcher never updates itself. Add a Linux job to
`.github/workflows/launcher-windows.yml` (or a sibling) that builds the AppImage with the updater key and adds the
`linux-x86_64` platform to `latest.json`.

## Done when

A Linux launcher on 0.6.x offers the next launcher release by itself.
