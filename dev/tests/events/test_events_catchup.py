"""Event sign-ups in a catch-up: a member who was away gets the calendar event before its sign-ups (Events'
SYNC.giveSort, which DigestSync uses for a want list, the items it answers with and the gives of a digest), and a
sign-up that arrives before its event is not pruned as an orphan while the event may still be on its way.

Run: luaenv\\Scripts\\python.exe tests\\events\\test_events_catchup.py [-k name]   (from dev)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "boot-ui"))
sys.path.insert(0, os.path.join(HERE, "..", "loot-roll"))
from _common import World, Client, case, run_all  # noqa: E402
import lr_common as lr  # noqa: E402

HELLO = 50
DAY = 86400


def guild(names):
    w = World()
    cs = []
    for i, n in enumerate(names):
        cs.append(Client(w, n, guild_rank=0 if i == 0 else 3, class_file="PALADIN" if i % 2 else "MAGE"))
    for c in cs:
        c.load_addon()
    w.tick(HELLO)
    return w, cs


def signups(c, occ):
    return c.eval_py("local st = ns.DB:GuildBucket('events', false); local out = {}; "
                     "for id, j in pairs(st and st.J or {}) do if j.o == ... and j.on then out[#out + 1] = j.by end end; "
                     "table.sort(out); return out", occ) or []


@case
def a_catch_up_gives_the_event_before_its_sign_ups():
    w, (gina, bert, cora) = guild(["Gina", "Bert", "Cora"])
    cora.logout()
    w.tick(2)
    occ = gina.eval_py("local d = ns.Events:NewDef(true); assert(ns.Events:SaveDef(d)); "
                       "return ns.Events:Schedule(d.id, GetServerTime() + 2 * 86400)")
    w.tick(3)
    assert bert.eval("return (ns.Events:SignUp(..., true))", occ) is True
    assert gina.eval("return (ns.Events:SignUp(..., true))", occ) is True
    w.tick(3)
    mark = len(w.addon_log)
    cora.login()
    w.tick(HELLO + 40)
    gives = lr.msgs_of_type(w, "EVG", mark, whole=True)        # (EVG: whispered gives, all to Cora here)
    kinds = [m["k"] for m in gives if m.get("k") in ("O", "J")]
    assert "O" in kinds and "J" in kinds, kinds
    assert kinds.index("O") < kinds.index("J"), kinds
    assert signups(cora, occ) == ["Bert-Thunderstrike", "Gina-Thunderstrike"], signups(cora, occ)
    w.assert_no_errors()


@case
def prune_keeps_a_sign_up_whose_event_is_on_its_way():
    w, (gina, bert) = guild(["Gina", "Bert"])
    res = bert.eval_py("""
        local st = ns.DB:GuildBucket('events', true)
        for _, k in ipairs({ "C", "D", "J", "K", "O", "R", "T" }) do st[k] = st[k] or {} end
        local now = GetServerTime()
        st.J["onew/x"] = { id = "onew/x", by = "Gina-Thunderstrike", rev = now, o = "onew", on = true, at = now }
        st.J["oold/x"] = { id = "oold/x", by = "Gina-Thunderstrike", rev = now - 90 * 86400, o = "oold", on = true,
                           at = now - 90 * 86400 }
        ns.Events:Prune(now)
        return { new = st.J["onew/x"] ~= nil, old = st.J["oold/x"] ~= nil }""")
    # (an event not here yet: its sign-up waits; one older than any event is kept: dropped)
    assert res == {"new": True, "old": False}, res
    w.assert_no_errors()


if __name__ == "__main__":
    run_all()
