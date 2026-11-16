---
tags: [log]
updated: 2026-11-16
---

# Decision Log

| Date | Decision | Why |
|---|---|---|
| 2026-11-16 | Start from release 1.5.5, not the original trunk | 1.5.5 is what the guild runs; the 57 unreleased commits after it are untested in the guild. Kept on `upstream-1.6.0` |
| 2026-11-16 | `main` = release tree, `dev` = source, in one repo | Members see the releases on the default branch; the source needs a branch of its own because the release tree holds only packaged files |
| 2026-11-16 | Keep the original author's history as it is, credit them in README and Home | Attribution, and `git blame` keeps working |
| 2026-11-16 | Work goes feature branch > PR > `dev`; a release updates `main` | Same flow as the Forever repo |
