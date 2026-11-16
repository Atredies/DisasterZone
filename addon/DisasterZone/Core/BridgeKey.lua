if DisasterZoneBoot and DisasterZoneBoot.Run("Core/BridgeKey.lua", ...) then return end -- DisasterZone: public keys Discord bridge records are verified with (written by dz-server keygen).
-- The private halves live only with each guild's bot. Core/Bridge.lua explains the scheme.
local addonName, ns = ...

ns.BridgeKeys = ns.BridgeKeys or {}

-- Casual Disaster-Thunderstrike
ns.BridgeKeys["Casual Disaster-Thunderstrike"] = {
    seed = "def4d2b93a8e767d7d63a514d8ba4fc7",
    root = "a4aec9773adecc3bdcb5a8e0385dca4ca81a2257978079158b5ee8827dcc3c87",
    h = 16,
}
