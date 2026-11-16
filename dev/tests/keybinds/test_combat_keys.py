"""Keyboard handlers in combat: Frame:SetPropagateKeyboardInput is protected in combat on the modern clients (an addon
calling it then gets ADDON_ACTION_BLOCKED; upstream already guarded some calls with InCombatLockdown). Every call now
goes through Util.SetPropagateKeys, which does nothing in combat and applies the last value asked for when combat
ends. Here the mock's raw call is wrapped to record any call made in combat.

The sweep opens every page of the main window in combat (a page built for the first time during a fight), and presses
keys on every frame that has an OnKeyDown script in combat, then checks no raw call happened in combat.

Run: luaenv\\Scripts\\python.exe tests\\keybinds\\test_combat_keys.py [-k name]   (from dev)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(TESTS, "boot-ui"))

from _common import case, run_all, no_errors  # noqa: E402
from harness import World, Client  # noqa: E402

PAGES = ["home", "raids", "mybis", "gearsim", "consumables", "wardrobe", "atlas", "members", "map", "events", "polls",
         "recruit", "games", "council", "lootrules", "mylog"]

# Records a raw SetPropagateKeyboardInput made in combat (the mock copies methods per widget kind: wrapped in each).
GUARD = r"""
__inCombatCalls = {}
local n = 0
for _, mt in pairs(__MOCK.Methods) do
  local raw = rawget(mt, "SetPropagateKeyboardInput")
  if raw then
    n = n + 1
    rawset(mt, "SetPropagateKeyboardInput", function(self, v)
      if InCombatLockdown() then __inCombatCalls[#__inCombatCalls + 1] = tostring(self.GetName and self:GetName() or "?") end
      return raw(self, v)
    end)
  end
end
return n > 0
"""

PRESS_ALL = r"""
local key = ...
local n = 0
for _, f in ipairs(__MOCK.all_objects) do
  local st = __MOCK.OBJ[f]
  local fn = st and st.scripts and st.scripts.OnKeyDown
  if fn and f.IsVisible and f:IsVisible() then
    n = n + 1
    __MOCK.safecall("OnKeyDown", fn, f, key)
  end
end
return n
"""


def gm():
    w = World()
    c = Client(w, "Gina", class_file="WARRIOR", guild_rank=0)
    c.load_addon()
    w.tick(5)
    assert c.eval(GUARD) is True, "could not wrap the mock's SetPropagateKeyboardInput"
    return w, c


@case
def the_helper_waits_out_combat():
    w, c = gm()
    c.eval("__f = CreateFrame('Frame')")
    assert c.eval("return ns.Util.SetPropagateKeys(__f, true)") is True
    c.set_combat(True)
    assert c.eval("return ns.Util.SetPropagateKeys(__f, false)") is False
    assert c.eval("return __MOCK.OBJ[__f].propagate") is True          # (not changed in combat)
    c.set_combat(False)
    assert c.eval("return __MOCK.OBJ[__f].propagate") is False         # applied when combat ended
    assert c.eval("return ns.Util.SetPropagateKeys(__f, true)") is True
    assert not c.eval_py("return __inCombatCalls"), c.eval_py("return __inCombatCalls")
    no_errors(w)


@case
def pages_first_opened_in_combat():
    w, c = gm()
    c.set_combat(True)
    for page in PAGES:
        c.eval("ns.MainFrame:Open(...)", page)
        w.tick(0.3)
    assert not c.eval_py("return __inCombatCalls"), c.eval_py("return __inCombatCalls")
    no_errors(w)


@case
def keys_on_every_page_in_combat():
    w, c = gm()
    pressed = 0
    for page in PAGES:
        c.eval("ns.MainFrame:Open(...)", page)
        w.tick(0.5)
        c.set_combat(True)
        for key in ("A", "ESCAPE", "ENTER", "LEFT"):
            pressed += c.eval(PRESS_ALL, key)
        c.set_combat(False)
        w.tick(0.2)
    assert pressed > 0, "no key handler was reached"
    assert not c.eval_py("return __inCombatCalls"), c.eval_py("return __inCombatCalls")
    no_errors(w)


if __name__ == "__main__":
    run_all()
