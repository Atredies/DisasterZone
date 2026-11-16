"""Authority holes, round 4 (2026-11-09, after test_authority.py / 2 / 3): every case is a guild member sending a
hand-made message, the other clients refusing it (or naming who passed it on), and the legitimate flow still working.
A receiver believes only the actual sender, never an author / owner / host named inside the payload.

  1. Feedback (FBN / FBR): items, me-toos and replies are believed from their author or staff. Passed on by anyone
     else, a new one is kept marked with who passed it on (shown on the item), and it never changes or withdraws one
     the receiver holds; the author's copy is asked for and clears the mark.
  2. Live events (EVS): the host is the sender (or a hand-over the host I know sent); a client never goes on hosting
     a run, nor publishes its result, because a message named it.
  3. Group runs (DRS): a run in the board digest is taken from its owner only; a relayed one is asked for from its
     owner, and a run never changes owner.
  4. Professions (PFB / PFR): a member's record (professions, gear, main / alt link) is believed from its owner or an
     officer; the officer-only main link only from an officer. A relayed copy is asked for from them.
  5. Low priority: the developer's feedback plan only from the developer; a council Ledger entry's `by`.

Run: luaenv\\Scripts\\python.exe tests\\sync\\test_authority4.py [-k name]   (from dev)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TESTS, "boot-ui"))

from _common import World, Client, case, run_all, no_errors  # noqa: E402

FB_REALM = "Thunderstrike"


def fk(name):
    return "%s-%s" % (name, FB_REALM)


# ------------------------------------------------------------------------------------------------------------------
# 1. Feedback
# ------------------------------------------------------------------------------------------------------------------
def fb_world():
    """Gina the GM, Olaf an officer, Arakis the developer, Alfa / Bert / Cleo raiders (as tests/feedback)."""
    w = World()
    c = {}
    for name, cls, rank in (("Gina", "PALADIN", 0), ("Olaf", "WARRIOR", 1), ("Arakis", "PALADIN", 3),
                            ("Alfa", "MAGE", 3), ("Bert", "ROGUE", 3), ("Cleo", "PRIEST", 3)):
        c[name] = Client(w, name, class_file=cls, guild_rank=rank)
    for x in c.values():
        x.load_addon()
    w.tick(3)
    w.tick(40, step=0.25)
    return w, c


def fb_item(cl, id_):
    return cl.eval_py("local v = ns.Feedback:Get(...); if not v then return nil end; return { text = v.text, "
                      "gone = v.gone, via = v.via or false, votes = v.voteCount, author = v.author }", id_)


FB_SEND = ("local id, rec, to = ...; ns.Comm:Send({ t = 'FBN', r = { [id] = rec } }, to and 'WHISPER' or 'GUILD', to, "
           "'fb')")


def fb_rec(cl, id_):
    return cl.eval_py("local s = ns.DB:GuildBucket('feedback', false, ns.Util.GuildKey()); return s and s.r[...]", id_)


@case
def feedback_an_item_made_up_in_someones_name_is_marked_with_who_passed_it_on():
    w, c = fb_world()
    alfa, bert, gina = c["Alfa"], c["Bert"], c["Gina"]
    now = alfa.eval("return GetServerTime()")
    fid = fk("Alfa") + "#7"
    forged = {"k": "i", "a": fk("Alfa"), "n": 7, "kd": "love", "x": "Bert is the best tank", "t": now, "rv": now}
    alfa.logout()          # (the author away: nobody to confirm it)
    w.tick(2)
    bert.eval(FB_SEND, fid, forged, fk("Gina"))
    w.tick(3)
    got = fb_item(gina, fid)
    assert got and got["via"] == fk("Bert"), got
    no_errors(w)


@case
def feedback_a_relayed_withdrawal_or_edit_never_changes_an_item_held():
    w, c = fb_world()
    alfa, bert, gina, olaf, cleo = c["Alfa"], c["Bert"], c["Gina"], c["Olaf"], c["Cleo"]
    fid = alfa.eval("local id = ns.Feedback:Submit('bug', 'The roll popup closes in combat.'); return id")
    assert fid == fk("Alfa") + "#1", fid
    w.tick(5)
    assert fb_item(gina, fid)["via"] is False
    # Bert withdraws it, and rewrites it, on Gina's and Cleo's clients (newer versions "by" Alfa)
    rec = fb_rec(bert, fid)
    gone = {"k": "i", "a": fk("Alfa"), "n": 1, "d": 1, "rv": rec["rv"] + 50}
    bert.eval(FB_SEND, fid, gone, fk("Gina"))
    edit = dict(rec, x="Please remove the roll popup entirely", rv=rec["rv"] + 60)
    bert.eval(FB_SEND, fid, edit, fk("Cleo"))
    w.tick(5)
    for x in (gina, cleo):
        got = fb_item(x, fid)
        assert got and not got["gone"] and got["text"] == "The roll popup closes in combat." and got["via"] is False, \
            (x.name, got)
    # a me-too Gina gave, taken back by Bert in her name: refused
    assert gina.eval("return (ns.Feedback:Vote(...))", fid, True) is True
    w.tick(5)
    assert fb_item(cleo, fid)["votes"] == 1
    vid = fid + "+" + fk("Gina")
    v = fb_rec(bert, vid)
    bert.eval(FB_SEND, vid, dict(v, d=1, rv=v["rv"] + 30), fk("Cleo"))
    w.tick(5)
    assert fb_item(cleo, fid)["votes"] == 1
    # an officer passing on the author's own withdrawal: taken (staff only hold copies vouched for)
    olaf.eval(FB_SEND, fid, gone, fk("Cleo"))
    w.tick(3)
    assert fb_rec(cleo, fid).get("d") == 1 and fb_item(cleo, fid) is None
    # the author's own withdrawal reaches everyone
    assert alfa.eval("return (ns.Feedback:Withdraw(...))", fid) is True
    w.tick(5)
    for x in (gina, bert):
        assert fb_rec(x, fid).get("d") == 1, x.name
    no_errors(w)


@case
def feedback_passed_on_by_a_member_reaches_the_developer_marked_until_the_author_confirms():
    w, c = fb_world()
    for n in ("Gina", "Olaf", "Arakis", "Cleo"):
        c[n].logout()
    w.tick(5)
    alfa, bert, dev = c["Alfa"], c["Bert"], c["Arakis"]
    fid = alfa.eval("local id = ns.Feedback:Submit('idea', 'Show who still needs a token.'); return id")
    w.tick(5)
    assert fb_item(bert, fid)["via"] is False          # (first hand from Alfa)
    alfa.logout()
    w.tick(3)
    dev.login()
    w.tick(60, step=0.25)
    got = fb_item(dev, fid)
    assert got and got["text"] == "Show who still needs a token." and got["via"] == fk("Bert"), got
    # (the developer numbered it: Bert hears the number)
    assert dev.eval_py("return ns.Feedback:Get(...).no", fid) == 1
    # the author comes back: the developer's client asks them and the mark goes
    alfa.login()
    w.tick(60, step=0.25)
    dev.eval("ns.Feedback:SyncNow(...)", fk("Alfa"))
    w.tick(10, step=0.25)
    got = fb_item(dev, fid)
    assert got["via"] is False, got
    no_errors(w)


if __name__ == "__main__":
    run_all()
