"""Sync notices: what a member sees and knows when sync can't do its job quietly.

  * a BiS list this client can't read is said once per player per session (Store:Put), not only in a debug line;
  * a late login learns the versions of who was already online (V, whispered back to its login HELLO);

Run: luaenv\\Scripts\\python.exe tests\\sync\\test_sync_notices.py [-k name]   (from dev)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "boot-ui"))

from _common import World, Client, case, run_all, solo, no_errors  # noqa: E402


@case
def a_list_this_client_cannot_read_is_said_once():
    """A council refused a member's whole BiS list (an item it could not read) with only a debug line, and the owner
    saw "people on the old version don't sync". Store:Put now prints why, once per player per session."""
    w, c = solo("Cou", guild_rank=1, tick=3, council=["Cou"], phase=3, members=[("Bob", "MAGE", 3)])
    n = len(c.chat_frame)
    put = """local d = { v = 1, cl = 'MAGE', sp = '', ph = { [1] = { [1] = { 5000000, 0 } } }, ob = {}, eq = {} }
      return ns.Store:Put('Bob-Thunderstrike', { r = %d, ts = GetServerTime(), h = ns.Util.Hash(d), d = d }, 'direct')"""
    assert c.eval(put % 1) is False
    assert c.eval(put % 2) is False
    said = [line for line in c.chat_frame[n:] if "Couldn't take" in line]
    assert len(said) == 1 and "Bob" in said[0] and "/dz version" in said[0], c.chat_frame[n:]
    no_errors(w)


@case
def a_late_login_learns_the_versions_of_who_was_already_online():
    """Versions travel in the login HELLO. Somebody who logs in after me never heard mine, so their roster kept the
    version it saved earlier. My copy now whispers my version back to a login HELLO it hears."""
    w = World()
    gm = Client(w, "Gina", class_file="WARRIOR", guild_rank=0)
    missy = Client(w, "Missy", class_file="HUNTER", guild_rank=1)
    gm.load_addon()
    w.tick(30)                                                        # (the GM's own HELLO is long gone)
    missy.load_addon()
    gm_key = "Gina-Thunderstrike"
    # what Missy's saved peers said about the GM before she logged in
    missy.eval("ns.db.peers[...] = { v = '0.0.1', lastSeen = 0 }", gm_key)
    w.tick(40)
    assert missy.eval("return ns.Sync:GetPeer(...).v", gm_key) == gm.eval("return ns.version")
    no_errors(w)


if __name__ == "__main__":
    run_all()
