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
| 2026-11-16 | The developer is a name AND realm key (`Util.DEV_KEY`), not a name | After the handover anyone could take the old developer's name on a connected realm and get the developer's powers |
| 2026-11-16 | Refuse the original update and bot keys; ship our own update key | Their private halves are lost: an update or bot record signed with them could come from anybody |
| 2026-11-16 | No signature re-check of a stored update at load (Adler-32 stays) | The stored update sits in the member's own saved variables: whoever can write there can edit the addon's files too, so a load-time signature check adds no protection |
