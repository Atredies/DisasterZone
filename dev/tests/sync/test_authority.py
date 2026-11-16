"""Authority holes (pass 1 and 2 of the trust review): every case is a guild member sending a hand-made message, and
every other client refusing it.

  1. GM rules: an officer's RLL that names the GM as author (lrb / arb / dcb / rcb) no longer changes the loot,
     attendance, Discord or recruitment rules; a GMR is taken only from the Guild Master (rank 0) as its sender.

Run: luaenv\\Scripts\\python.exe tests\\sync\\test_authority.py [-k name]   (from dev)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(TESTS, "boot-ui"))
sys.path.insert(0, os.path.join(TESTS, "raidplan"))
sys.path.insert(0, os.path.join(TESTS, "reserves"))

from _common import case, run_all, no_errors  # noqa: E402
from harness import World, Client  # noqa: E402

REALM = "Thunderstrike"


def key(name):
    return "%s-%s" % (name, REALM)


def guild():
    """Gina = GM, Missy = officer (rank 1), Aurel = rank 2, Nala = rank 3."""
    w = World()
    cs = {}
    for name, cls, rank in (("Gina", "WARRIOR", 0), ("Missy", "HUNTER", 1), ("Aurel", "MAGE", 2),
                            ("Nala", "PRIEST", 3)):
        c = Client(w, name, class_file=cls, guild_rank=rank)
        c.load_addon()
        cs[name] = c
    w.tick(5)
    return w, cs


def rules(c):
    return c.eval_py("return { lr = ns.Guild:GetLootRules(), ar = ns.Guild:GetAttendanceRules(), "
                     "dc = ns.Guild:GetDiscord().host, rc = ns.Guild:GetRecruitRules().uc }")


# ------------------------------------------------------------------------------------------------------------------
# 1. GM rules
# ------------------------------------------------------------------------------------------------------------------
@case
def an_officer_cannot_forge_the_gms_rules():
    w, c = guild()
    gm, missy, nala = c["Gina"], c["Missy"], c["Nala"]
    before = rules(nala)
    # an officer's raid leaders list (legitimate: officers keep it) carrying "the GM's" rules
    missy.eval("local me, gm = ...; ns.Comm:Send({ t = 'RLL', rev = GetServerTime() + 5, m = { me }, by = me, "
               "ar = { o = 1, d = 1 }, arb = gm, lr = { f = 90, s = 'p', l = 'r', w = 'd', y = 'a', o = 0, q = 's' }, "
               "lrb = gm, dc = { h = me }, dcb = gm, rc = { uc = 29 }, rcb = gm }, 'GUILD', nil, 'ctrl')",
               key("Missy"), key("Gina"))
    w.tick(3)
    assert nala.eval_py("return ns.Guild:GetRaidLeadersInfo().members") == [key("Missy")]
    assert rules(nala) == before, rules(nala)
    # the GM's own record, sent by an officer (or a member): refused too
    for forger in (missy, nala):
        forger.eval("ns.Comm:Send({ t = 'GMR', v = GetServerTime() + 30, ar = { o = 2, d = 2 }, dc = { h = ... } }, "
                    "'GUILD', nil, 'ctrl')", key(forger.name))
        w.tick(3)
        assert rules(nala) == before, rules(nala)
    assert missy.eval("return (ns.Guild:SetLootRules({ f = 50, s = 'r', l = 'l', w = 'r', y = 'n' }))") is False
    # the GM's change reaches everyone, and an officer's later list keeps it
    assert gm.eval("return (ns.Guild:SetAttendanceRules(12, 20))") is True
    assert gm.eval("return (ns.Guild:SetDiscord({ host = ... }))", key("Aurel")) is True
    w.tick(3)
    assert nala.eval_py("return ns.Guild:GetAttendanceRules()") == {"o": 12, "d": 20}
    assert nala.eval("return ns.Guild:GetDiscord().host") == key("Aurel")
    missy.eval("local nala, me, gm = ...; ns.Comm:Send({ t = 'RLL', rev = GetServerTime() + 50, m = { nala }, by = me, "
               "dc = { h = me }, dcb = gm }, 'GUILD', nil, 'ctrl')", key("Nala"), key("Missy"), key("Gina"))
    w.tick(3)
    assert nala.eval("return ns.Guild:GetDiscord().host") == key("Aurel")
    assert nala.eval("return ns.Guild:IsDiscordHost(...)", key("Missy")) is False
    no_errors(w)


@case
def a_member_who_missed_the_gm_gets_the_rules_from_the_gm_only():
    w, c = guild()
    gm, nala = c["Gina"], c["Nala"]
    nala.logout()
    assert gm.eval("return (ns.Guild:SetAttendanceRules(7, 9))") is True
    w.tick(3)
    gm.logout()
    nala.login()
    w.tick(60)
    # only the officers were online: the GM's rules can't be vouched for by anybody else
    assert nala.eval_py("return ns.Guild:GetAttendanceRules()") == {"o": 5, "d": 10}
    gm.login()
    w.tick(60)
    assert nala.eval_py("return ns.Guild:GetAttendanceRules()") == {"o": 7, "d": 9}
    no_errors(w)


if __name__ == "__main__":
    run_all()
