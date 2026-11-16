---
title: "Port Forever's test fixes (baseline to 0 failed)"
tags: [task]
status: 5 - Done
priority: p1
effort: S
completed: 2026-11-16
updated: 2026-11-16
---

# Port Forever's test fixes

The 5 suites failing on 1.5.5 ([[Linux Dev Setup]]) are upstream test bugs. The Forever repo fixed them (its PR #21
and the font fallback in `dev/tools/ui_audit.py`). Bring those fixes over first, so every later change has a clean
baseline. Forever's fixes for `test_boot`, `test_changelog`, `test_naxx` are not needed here: those pass on 1.5.5.

## Done when

`DZ_FORK=0 run_all.py --all` reports 0 failed on Linux on `dev`.

## Done 2026-11-16

The font fallback and noon pins came over as they were; `test_mixed_versions` needed its own fix (the release tree's
`release-1.4.0` tag has no source). Forever's `ui_audit_states.py` fix did not apply: that broken merge is 1.6.0-only.
