"""Sync notices: what a member sees and knows when sync can't do its job quietly.

  * a BiS list this client can't read is said once per player per session (Store:Put), not only in a debug line;

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


if __name__ == "__main__":
    run_all()
