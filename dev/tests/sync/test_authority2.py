"""Authority holes, round 2 (after the first round in test_authority.py): every case is a guild member sending a
hand-made message, every other client refusing it (or naming who passed it on), and the legitimate flow still working.

  1. Raid sign-ups: a sign-up (or a change / withdrawal of one) passed on (RPG) by a plain member is not taken; the
     owner's, a raid planner's or the raid's own leader's copy is. A held-back copy is asked for from the owner and a
     planner who are online, so every client still ends up with the real answer. (Team waitlists the same.)

Run: luaenv\\Scripts\\python.exe tests\\sync\\test_authority2.py [-k name]   (from dev)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TESTS, "boot-ui"))
sys.path.insert(0, os.path.join(TESTS, "raidplan"))
sys.path.insert(0, os.path.join(TESTS, "reserves"))

from _common import case, run_all, no_errors  # noqa: E402
from harness import World, Client  # noqa: E402

REALM = "Thunderstrike"


def key(name):
    return "%s-%s" % (name, REALM)


def guild():
    """Gina = GM, Missy = officer (rank 1), Aurel = rank 2, Nala = rank 3 (as test_authority.py)."""
    w = World()
    cs = {}
    for name, cls, rank in (("Gina", "WARRIOR", 0), ("Missy", "HUNTER", 1), ("Aurel", "MAGE", 2),
                            ("Nala", "PRIEST", 3)):
        c = Client(w, name, class_file=cls, guild_rank=rank)
        c.load_addon()
        cs[name] = c
    w.tick(5)
    return w, cs


# ------------------------------------------------------------------------------------------------------------------
# 1. Raid sign-ups
# ------------------------------------------------------------------------------------------------------------------
def _signups(cl, occ):
    return cl.eval_py("local r = ns.db.raidplan and ns.db.raidplan[ns.Guild:GetGuildKey()]; return r and r.U[...]", occ) or {}


def _forge_rpg(frm, to, occ, who, st, bump=10, wipe_e=False):
    """frm whispers `to` a hand-made RPG of occurrence occ: who's answer st, newer than any they hold."""
    frm.eval("local o, to, who, st, bump = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; "
             "local cur = r.U[o] and r.U[o][who]; local s = { st = st, rev = (cur and cur.rev or GetServerTime()) + bump, "
             "c = 'WARRIOR' }; s.at = cur and cur.at or s.rev; "
             "ns.Comm:Send({ t = 'RPG', o = o, u = { [who] = s } }, 'WHISPER', to, 'data')", occ, to, who, st, bump)


@case
def a_relayed_sign_up_is_taken_only_from_its_owner_or_a_planner():
    from rp_common import world as rp_world, create, now, DAY, K, signup
    w, c = rp_world()
    gina, bob, lee, rita, sam = c["Gina"], c["Bob"], c["Lee"], c["Rita"], c["Sam"]   # Gina GM, Bob planner
    occ = create(bob, i="kara", t=now(bob) + DAY)
    w.tick(3)
    assert signup(lee, occ, "A")["ok"] is True
    w.tick(3)
    assert _signups(sam, occ)[K("Lee")]["st"] == "A"
    # Rita withdraws Lee's answer on Sam's client (a newer "X"), and signs Gina up there
    _forge_rpg(rita, K("Sam"), occ, K("Lee"), "X")
    _forge_rpg(rita, K("Sam"), occ, K("Gina"), "A")
    w.tick(10)
    u = _signups(sam, occ)
    assert u[K("Lee")]["st"] == "A", u
    assert K("Gina") not in u, u
    # (and the raid's sign-up list shows Lee only)
    assert set(sam.eval_py("return ns.RaidPlan:GetSignups(...)", occ)) == {K("Lee")}
    # the planner passes on a real change: taken
    assert signup(lee, occ, "T")["ok"] is True
    w.tick(3)
    assert _signups(sam, occ)[K("Lee")]["st"] == "T"
    sam.eval("local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; r.U[...] = nil", occ)
    bob.eval("local o, to = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; "
             "ns.Comm:Send({ t = 'RPG', o = o, e = r.E[o], u = r.U[o] }, 'WHISPER', to, 'data')", occ, K("Sam"))
    w.tick(2)
    assert _signups(sam, occ)[K("Lee")]["st"] == "T"
    # the owner's own copy: taken
    sam.eval("local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; r.U[...] = nil", occ)
    lee.eval("local o, to = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; "
             "ns.Comm:Send({ t = 'RPG', o = o, u = r.U[o] }, 'WHISPER', to, 'data')", occ, K("Sam"))
    w.tick(2)
    assert _signups(sam, occ)[K("Lee")]["st"] == "T"
    # a plain member passes on the real answer to a client that lost it: the owner's copy is asked for at once (RPW)
    # and comes, so the clients still agree
    sam.eval("local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; r.U[...] = nil", occ)
    mark = len(w.addon_log)
    rita.eval("local o, to = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; "
              "ns.Comm:Send({ t = 'RPG', o = o, u = r.U[o] }, 'WHISPER', to, 'data')", occ, K("Sam"))
    w.tick(10)
    assert _signups(sam, occ)[K("Lee")]["st"] == "T"
    asks = [e for e in w.addon_log[mark:] if e["sender"] == K("Sam") and e["chat_type"] == "WHISPER"
            and K("Lee") in e.get("recipients", [])]
    assert asks, "Sam did not ask Lee"
    # with the owner and every planner away, the real answer passed on by a member waits for the owner's login
    sam.eval("local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; r.U[...] = nil", occ)
    for x in (gina, bob, lee):
        x.logout()
    w.tick(2)
    rita.eval("local o, to = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; "
              "ns.Comm:Send({ t = 'RPG', o = o, u = r.U[o] }, 'WHISPER', to, 'data')", occ, K("Sam"))
    w.tick(10)
    assert K("Lee") not in _signups(sam, occ)
    lee.login()
    w.tick(60)
    assert _signups(sam, occ)[K("Lee")]["st"] == "T"
    no_errors(w)


@case
def a_withdrawal_passed_on_while_owner_and_planners_are_away_waits():
    from rp_common import world as rp_world, create, now, DAY, K, signup
    w, c = rp_world()
    gina, bob, lee, rita, sam = c["Gina"], c["Bob"], c["Lee"], c["Rita"], c["Sam"]
    occ = create(bob, i="kara", t=now(bob) + DAY)
    w.tick(3)
    assert signup(lee, occ, "A")["ok"] is True
    w.tick(3)
    for x in (gina, bob, lee):
        x.logout()
    w.tick(2)
    _forge_rpg(rita, K("Sam"), occ, K("Lee"), "X")
    w.tick(20)
    assert _signups(sam, occ)[K("Lee")]["st"] == "A"
    # nobody may vouch for it when the planner is back either (Rita passed it on, not the planner)
    bob.login()
    w.tick(60)
    assert _signups(sam, occ)[K("Lee")]["st"] == "A"
    no_errors(w)


@case
def a_relayed_waitlist_entry_is_taken_only_from_its_player_or_a_writer():
    from rp_common import world as rp_world, team, K
    w, c = rp_world()
    bob, lee, rita, sam = c["Bob"], c["Lee"], c["Rita"], c["Sam"]
    tid = team(bob, "Main", ["Lee"])
    w.tick(3)
    ln = "main"          # (a lineup id; the waitlists are kept per lineup id, Lineup.MergeWait)
    # Rita passes on Bob's team with a waitlist entry "by" Sam, joining it
    rita.eval("local tid, ln, sam, to = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; local now = GetServerTime(); "
              "ns.Comm:Send({ t = 'RPG', T = r.T[tid], w = { [ln] = { [sam] = { rev = now, by = sam, at = now } } } }, "
              "'WHISPER', to, 'data')", tid, ln, K("Sam"), K("Lee"))
    w.tick(3)

    def waiting(cl):
        return cl.eval_py("local tid, ln, k = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; "
                          "return r.W[tid] and r.W[tid][ln] and r.W[tid][ln][k] or false", tid, ln, K("Sam"))

    assert waiting(lee) is False, waiting(lee)
    # Sam's own copy (or the council's) is taken
    sam.eval("local tid, ln, sam, to = ...; local r = ns.db.raidplan[ns.Guild:GetGuildKey()]; local now = GetServerTime(); "
             "ns.Comm:Send({ t = 'RPG', T = r.T[tid], w = { [ln] = { [sam] = { rev = now, by = sam, at = now } } } }, "
             "'WHISPER', to, 'data')", tid, ln, K("Sam"), K("Lee"))
    w.tick(3)
    assert waiting(lee) and waiting(lee)["by"] == K("Sam"), waiting(lee)
    no_errors(w)


if __name__ == "__main__":
    run_all()
