"""The original author's keys (up to 1.5.5) are refused: their private halves are lost, so an in-game update or a
Discord bot record signed with one could come from anybody (Core/Patch.lua UNTRUSTED_ROOTS, Core/Bridge.lua Verify,
dev/tools/release.py refuse_untrusted).

Run: luaenv/bin/python tests/patch/test_untrusted_keys.py [-k name]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "boot-ui"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))

from _common import case, run_all, World, Client  # noqa: E402

import release  # noqa: E402

OLD_UPDATE = "9b703655eeb0f04ab4c8da1bdbc16cb8dbaa5fe4e0afd1dac7fa179dce7d605d"
OLD_BOT = "93ed344536965f6d3a9fb3e10f8972406bf14af6284a1313f2a0da94ec6ff106"


def one():
    w = World()
    c = Client(w, "Gina", guild_rank=0)
    c.load_addon()
    w.tick(3)
    return w, c


@case
def the_shipped_update_key_is_ours_and_taken():
    w, c = one()
    root = c.eval("return ns.PatchKey.root")
    assert root not in (OLD_UPDATE, OLD_BOT), root
    assert c.eval("return ns.Patch._Key() ~= nil") is True
    w.assert_no_errors()


@case
def the_original_keys_are_refused_in_game():
    w, c = one()
    for root in (OLD_UPDATE, OLD_BOT, OLD_UPDATE.upper()):
        assert c.eval("return ns.Patch.IsUntrustedKey({ root = '%s' })" % root) is True, root
        c.eval("ns.PatchKey = { seed = string.rep('a', 32), root = '%s', h = 10 }" % root)
        assert c.eval("return ns.Patch._Key() == nil") is True, root   # in-game updates off with such a key
    w.assert_no_errors()


@case
def the_release_tool_refuses_them():
    for root in (OLD_UPDATE, OLD_BOT):
        try:
            release.refuse_untrusted(root, "test")
        except release.ReleaseError:
            continue
        raise AssertionError("release.py took %s" % root[:8])
    release.refuse_untrusted("9b1288d405487f654f9d1c030baf8aa6bb202def27bdc44ff7b13e344290e1f5", "ours")


if __name__ == "__main__":
    run_all()
