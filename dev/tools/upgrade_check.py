"""Upgrade check: does this build keep a member's data? Loads a real saved-variables file (WTF/Account/<account>/
SavedVariables/DisasterZone.lua, written by an older release such as 1.5.5) into this build in the mock client, runs
two logins and a logout, and compares every saved variable before and after: what each top-level table holds and how
many entries, recursively. A drop in entries is reported as a possible loss.

It reads the file and prints counts and key names only, never values. The file stays where it is (pass a copy).

Run (from dev/):
  luaenv/bin/python tools/upgrade_check.py <path to DisasterZone.lua> [--name Arakis] [--realm Thunderstrike]
                                                                       [--guild "Casual Disaster"] [--rank 0]
Exit code 0 when nothing was lost, 1 otherwise.
"""
import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lupa  # noqa: E402

import harness  # noqa: E402

SV_NAMES = ("DisasterZoneDB", "DisasterZonePatchDB", "DisasterZoneLogDB", "DisasterZoneMeterDB",
            "DisasterZoneBossLearnDB", "DisasterZoneBridgeDB")


def split_saved(src):
    """{name: Lua table source} from a SavedVariables file: one 'Name = { ... }' block per variable."""
    out, starts = {}, [(m.start(), m.group(1)) for m in re.finditer(r"(?m)^([A-Za-z_][A-Za-z0-9_]*) = ", src)]
    for i, (pos, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(src)
        out[name] = src[pos:end].split(" = ", 1)[1].strip()
    return out


def shape(lua, src, depth=3):
    """{path: entry count} of a Lua table source, `depth` levels deep (table counts only, no values)."""
    rt = lua.eval("function(s) return (loadstring or load)('return ' .. s)() end")
    t = rt(src)
    out = {}

    def walk(x, path, d):
        if lupa.lua_type(x) != "table":
            return
        keys = list(x.keys())
        out[path or "."] = len(keys)
        if d == 0:
            return
        for k in keys:
            walk(x[k], "%s/%s" % (path, k), d - 1)

    walk(t, "", depth)
    return out


def guild_members(lua, db_src, guild, realm):
    """Character names (this realm) the saved data knows as guild members: keys of prof[<guild key>] and peers."""
    if not db_src:
        return set()
    t = lua.eval("function(s) return (loadstring or load)('return ' .. s)() end")(db_src)
    names = set()
    suffix = "-" + realm.replace(" ", "")
    for part in ("prof", "peers"):
        x = t[part]
        if lupa.lua_type(x) != "table":
            continue
        tables = [x[guild + suffix]] if part == "prof" else [x]
        for tb in tables:
            if lupa.lua_type(tb) != "table":
                continue
            for k in tb.keys():
                if isinstance(k, str) and k.endswith(suffix):
                    names.add(k[:-len(suffix)])
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--name", default="Arakis")
    ap.add_argument("--realm", default="Thunderstrike")
    ap.add_argument("--guild", default="Casual Disaster")
    ap.add_argument("--rank", type=int, default=0)
    a = ap.parse_args()
    with open(a.file, encoding="utf-8", errors="replace") as fh:
        before = split_saved(fh.read())
    missing = [n for n in SV_NAMES if n not in before]
    lua = lupa.LuaRuntime()

    # (the clock at now: the default test clock is in the past, and records dated after it look like the future)
    w = harness.World(realm=a.realm, server_time=int(time.time()))
    # The guild as the file knows it: everyone with a professions record or seen with DisasterZone (offline members
    # of the roster). Without them the addon tidies data about people it does not see in its guild, which is right
    # in game for people who left, and a false "loss" here.
    roster = guild_members(lua, before.get("DisasterZoneDB"), a.guild, a.realm) - {a.name}
    for name in sorted(roster):
        harness.Client(w, name, realm=a.realm, guild=a.guild, guild_rank=4, online=False)
    print("  roster seeded from the file: %d other member(s), offline" % len(roster))
    c = harness.Client(w, a.name, realm=a.realm, guild=a.guild, guild_rank=a.rank, class_file="WARRIOR")
    for name, src in before.items():
        c.set_saved_variable(name, src)
    c.load_addon()
    w.tick(30)
    c.relog()
    w.tick(30)
    after = c.saved_variables()
    errors = w.errors() if hasattr(w, "errors") else []

    lost = 0
    print("upgrade check: %s as %s-%s (%s, rank %d)" % (os.path.basename(a.file), a.name, a.realm, a.guild, a.rank))
    if missing:
        print("  not in the file (fine for a fresh install): %s" % ", ".join(missing))
    for name in SV_NAMES:
        if name not in before:
            continue
        if name not in after:
            print("  LOST  %s: gone after the upgrade" % name)
            lost += 1
            continue
        b, n = shape(lua, before[name]), shape(lua, after[name])
        drops = [(p, b[p], n.get(p, 0)) for p in sorted(b) if n.get(p, 0) < b[p]]
        grew = sum(1 for p in n if n[p] > b.get(p, 0))
        print("  %-24s %6d entries before, %6d after; %d path(s) grew" % (name, b.get(".", 0), n.get(".", 0), grew))
        for p, x, y in drops:
            print("      fewer: %-50s %d -> %d" % (p, x, y))
            lost += 1
    for e in errors or []:
        print("  LUA ERROR: %s" % str(e)[:200])
    print("result: %s" % ("nothing lost" if lost == 0 and not errors else "%d possible loss(es), %d error(s): read "
                                                                          "each one" % (lost, len(errors or []))))
    return 0 if lost == 0 and not errors else 1


if __name__ == "__main__":
    sys.exit(main())
