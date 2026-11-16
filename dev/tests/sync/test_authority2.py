"""Authority holes, round 2 (after the first round in test_authority.py): every case is a guild member sending a
hand-made message, every other client refusing it (or naming who passed it on), and the legitimate flow still working.

  1. Raid sign-ups: a sign-up (or a change / withdrawal of one) passed on (RPG) by a plain member is not taken; the
     owner's, a raid planner's or the raid's own leader's copy is. A held-back copy is asked for from the owner and a
     planner who are online, so every client still ends up with the real answer. (Team waitlists the same.)
  3. "by" labels: officer notes, guest book notes, recruit removals keep who passed them on when the sender is not
     the writer.
  4. LootReserve mirror: only the group's leader, its master looter (LootReserve's own rule) or the raid's loot
     authority host a session that becomes my read-only list.

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


def guild(aurel_rank=2):
    """Gina = GM, Missy = officer (rank 1), Aurel = rank 2 (or aurel_rank), Nala = rank 3 (as test_authority.py)."""
    w = World()
    cs = {}
    for name, cls, rank in (("Gina", "WARRIOR", 0), ("Missy", "HUNTER", 1), ("Aurel", "MAGE", aurel_rank),
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


# ------------------------------------------------------------------------------------------------------------------
# 3. "by" labels: officer notes, guest book, recruit removals
# ------------------------------------------------------------------------------------------------------------------
def _officers_guild():
    w, c = guild(aurel_rank=1)
    # Missy and Aurel are officers (rank 1), Nala is not
    for n in ("Missy", "Aurel"):
        assert c["Nala"].eval("return ns.Guild:IsOfficer(..., true)", key(n)) is True, n
    return w, c


@case
def an_officer_note_passed_on_names_who_passed_it():
    w, c = _officers_guild()
    gm, missy, aurel = c["Gina"], c["Missy"], c["Aurel"]
    target = key("Nala")
    send = ("local k, n, v, by, to = ...; ns.Comm:Send({ t = 'ON', k = k, n = n, v = v, by = by }, 'WHISPER', to, "
            "'data')")
    rev = gm.eval("return GetServerTime()") + 5
    missy.eval(send, target, "Steals from the bank", rev, key("Gina"), key("Aurel"))
    w.tick(3)
    note = aurel.eval_py("return ns.OfficerNotes:Get(...)", target)
    assert note["by"] == key("Gina") and note["via"] == key("Missy"), note
    # the same note from its writer clears the mark
    gm.eval(send, target, "Steals from the bank", rev, key("Gina"), key("Aurel"))
    w.tick(3)
    note = aurel.eval_py("return ns.OfficerNotes:Get(...)", target)
    assert note["by"] == key("Gina") and "via" not in note, note
    # a note the GM writes reaches the officers first hand
    assert gm.eval("return (ns.OfficerNotes:Set(..., 'Healer, raids twice a week'))", key("Aurel")) is True
    w.tick(3)
    note = missy.eval_py("return ns.OfficerNotes:Get(...)", key("Aurel"))
    assert note["text"] == "Healer, raids twice a week" and note["by"] == key("Gina") and "via" not in note, note
    no_errors(w)


@case
def a_guest_book_note_passed_on_names_who_passed_it():
    w, c = _officers_guild()
    gm, missy, aurel = c["Gina"], c["Missy"], c["Aurel"]
    pug = "Pugzor-Thunderstrike"
    missy.eval("local pug, gm = ...; local now = GetServerTime() + 5; ns.Comm:Send({ t = 'GNL', rev = now, by = gm, "
               "l = { { k = pug, n = 'Ninja looter', b = gm, a = now } } }, 'GUILD', nil, 'data')", pug, key("Gina"))
    w.tick(3)
    note = aurel.eval_py("return ns.GuestBook:GetNote(...)", pug)
    assert note["note"] == "Ninja looter" and note["by"] == key("Gina") and note["via"] == key("Missy"), note
    entry = aurel.eval_py("local e = ns.GuestBook:GetEntry(...); return e and { by = e.noteBy, via = e.noteVia }", pug)
    assert entry == {"by": key("Gina"), "via": key("Missy")}, entry
    # the GM's own note: no mark on anyone
    ok = gm.eval_py("return { ns.GuestBook:SetNote('Healbot-Thunderstrike', 'Great healer') }")
    assert ok[0] is True, ok
    w.tick(3)
    for x in (missy, aurel):
        note = x.eval_py("return ns.GuestBook:GetNote(...)", "Healbot-Thunderstrike")
        assert note["by"] == key("Gina") and "via" not in note, (x.name, note)
        # (and the relayed one kept its mark through the GM's newer list: the note itself did not change)
    note = aurel.eval_py("return ns.GuestBook:GetNote(...)", pug)
    assert note.get("via") == key("Missy") or note["by"] == key("Gina"), note
    no_errors(w)


@case
def a_recruit_removal_passed_on_names_who_passed_it():
    w, c = _officers_guild()
    gm, missy, aurel = c["Gina"], c["Missy"], c["Aurel"]
    assert aurel.eval("return ns.Recruit:IsRecruiter(...)", key("Missy")) is True
    who = "Recruitme-Thunderstrike"
    send = "local k, v, by, to = ...; ns.Comm:Send({ t = 'RCX', k = k, v = v, by = by }, 'WHISPER', to, 'data')"
    rev = gm.eval("return GetServerTime()") + 5
    missy.eval(send, who, rev, key("Gina"), key("Aurel"))
    w.tick(3)

    def tomb(cl):
        return cl.eval_py("local b = ns.DB:GuildBucket('recruit', false, ns.Util.GuildKey()); "
                          "return b and b.x and b.x[...]", who)

    x = tomb(aurel)
    assert x["by"] == key("Gina") and x["rb"] == key("Missy"), x
    gm.eval(send, who, rev, key("Gina"), key("Aurel"))
    w.tick(3)
    x = tomb(aurel)
    assert x["by"] == key("Gina") and "rb" not in x, x
    # a person record passed on "by" the GM, with a note "by" the GM
    missy.eval("local who, gm, to = ...; local now = GetServerTime() + 9; ns.Comm:Send({ t = 'RC', k = who, v = now, "
               "r = { st = 'talk', rev = now, by = gm, at = now, n = { { by = gm, at = now, t = 'Said yes' } } } }, "
               "'WHISPER', to, 'data')", "Newbie-Thunderstrike", key("Gina"), key("Aurel"))
    w.tick(3)
    p = aurel.eval_py("local b = ns.DB:GuildBucket('recruit', false, ns.Util.GuildKey()); return b.p[...]",
                      "Newbie-Thunderstrike")
    assert p["by"] == key("Gina") and p["rb"] == key("Missy") and p["n"][0]["rb"] == key("Missy"), p
    no_errors(w)


# ------------------------------------------------------------------------------------------------------------------
# 4. LootReserve mirror
# ------------------------------------------------------------------------------------------------------------------
SESSION = r"""
LootReserve.Server.CurrentSession = { Settings = { Blind = false, MaxReservesPerPlayer = 1, LootCategories = { 2010 },
  Duration = 0, Lock = false, Equip = false, Multireserve = 1 }, Duration = 0, StartTime = 100, AcceptingReserves = true,
  Members = { Hanna = { ReservesLeft = 0, ReservesDelta = 0 }, Carol = { ReservesLeft = 0, ReservesDelta = 0 } },
  ItemReserves = { [...] = { Players = { "Carol", "Hanna" } } }, ItemConditions = {} }
LootReserve.Comm:BroadcastSessionInfo(true)"""


@case
def a_raid_member_who_cannot_host_lootreserve_is_not_mirrored():
    from rv_common import reserve_raid, open_reserves, key as rkey
    from test_lootreserve import lr_client, lr_host, RUBY_DRAPE
    r = reserve_raid()
    hanna = lr_client(r, "Hanna", "PRIEST")          # a pug, neither leader nor master looter
    hanna.eval(SESSION, RUBY_DRAPE)
    r.w.tick(4)
    for n in ("Alice", "Carol"):
        assert r[n].eval_py("return ns.Reserves:IsForeign()") is None, n
        assert r[n].eval_py("return ns.Reserves:Get()") is None, n
    # nor does it make the DisasterZone host go quiet
    open_reserves(r, n=1)
    r.w.tick(3)
    assert r["Alice"].eval("return ns.ReserveLR.Hosting()")
    hanna.eval(SESSION, RUBY_DRAPE)
    r.w.tick(3)
    assert r["Alice"].eval("return ns.ReserveLR.Hosting()")
    assert r["Carol"].eval_py("return ns.Reserves:Get().by") == rkey("Alice")
    r.w.assert_no_errors()


@case
def the_master_looter_hosting_lootreserve_is_mirrored():
    from rv_common import reserve_raid, key as rkey
    from test_lootreserve import lr_host, RUBY_DRAPE
    r = reserve_raid()
    hanna = lr_host(r)
    hanna.eval(SESSION, RUBY_DRAPE)
    r.w.tick(4)
    for n in ("Alice", "Carol"):
        assert r[n].eval_py("return ns.Reserves:IsForeign()") == rkey("Hanna"), n
    r.w.assert_no_errors()


if __name__ == "__main__":
    run_all()
