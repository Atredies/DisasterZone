if DisasterZoneBoot and DisasterZoneBoot.Run("Core/PatchKey.lua", ...) then return end -- DisasterZone: public key in-game updates are verified with (written by dev/tools/release.py keygen).
-- The private half lives only on the publisher's machine. Core/Patch.lua explains the scheme.
local addonName, ns = ...

ns.PatchKey = {
    seed = "f59c3e54099958b6664309324484093f",
    root = "9b1288d405487f654f9d1c030baf8aa6bb202def27bdc44ff7b13e344290e1f5",
    h = 10,
}
