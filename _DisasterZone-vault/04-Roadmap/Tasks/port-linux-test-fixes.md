---
title: "Port Forever's test fixes (baseline to 0 failed)"
tags: [task]
status: 2 - Next up
priority: p1
effort: S
updated: 2026-11-16
---

# Port Forever's test fixes

The 5 suites failing on 1.5.5 ([[Linux Dev Setup]]) are upstream test bugs. The Forever repo fixed them (its PR #21
and the font fallback in `dev/tools/ui_audit.py`). Bring those fixes over first, so every later change has a clean
baseline. Forever's fixes for `test_boot`, `test_changelog`, `test_naxx` are not needed here: those pass on 1.5.5.

## Done when

`DZ_FORK=0 run_all.py --all` reports 0 failed on Linux on `dev`.
