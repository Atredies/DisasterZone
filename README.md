<p align="center">
  <img src="assets/banner.png" alt="DisasterZone - BiS lists, Loot Council, Raids, Strategy boards" width="100%">
</p>

<p align="center">
  <b>The guild addon of &lt;Casual Disaster&gt;</b> for the World of Warcraft TBC Anniversary realms.<br>
  <sub>Best-in-slot lists · a Loot Council that sees them · raid sign-ups and teams · strategy boards · and a few games on the side</sub>
</p>

<p align="center"><img src="assets/divider.png" width="70%" alt=""></p>

<h2 align="center">Download</h2>

<p align="center">
  <a href="https://github.com/Atredies/DisasterZone/releases/latest"><img src="assets/btn-zip.png" width="280" alt="Download the addon zip"></a>
</p>

<p align="center">
  Under <i>Assets</i>, click <b><code>DisasterZone-&lt;version&gt;.zip</code></b>. Don't use GitHub's green
  "Code &gt; Download ZIP" button: that gives you the release files, not the addon.
</p>

## Install

1. **Close the game.**
2. Open your WoW folder and go to `World of Warcraft\_anniversary_\Interface\AddOns`.
3. Unzip the zip into `AddOns`. The folders must sit **directly** in `AddOns`:

   ```
   AddOns\
     DisasterZone\               <- the addon (required)
       DisasterZone.toc
     DisasterZone_Rooms\         <- needed by Chess
     DisasterZone_Bingo\  DisasterZone_Chess\  ...   <- the game packs
   ```

   If you end up with `AddOns\DisasterZone-1.6.0\DisasterZone\...` (an extra folder level), move the inner folders up
   one level.
4. **Start the game.** On the character screen, click **AddOns** and make sure DisasterZone is ticked.
5. In game, type `/dz` to open it. `/dz version` shows which version you and your guildmates run.

## Coming from 1.5.5 or older (once)

1.6.0 is signed with new keys, so the old copies can't update to it by themselves. Install it by hand once:

1. Using the DisasterZone Launcher? Install **[Launcher 0.6.0](https://github.com/Atredies/DisasterZone/releases/tag/launcher-v0.6.0)**
   over the old one (it keeps your settings). Don't keep the old launcher: it follows the old release feed and would
   put the old version back. Then type `/launcher` once in the guild's Discord and paste the code in the launcher.
2. Close the game, **delete every `DisasterZone*` folder** in `AddOns`, then install as above.

Your raids, sign-ups, BiS lists, loot history and settings are kept: they live in your saved variables
(`WTF\Account\...\SavedVariables\DisasterZone.lua`), not in these folders. Don't delete the `WTF` folder.

## Updates

**From 1.6.0 on, updates come in game.** When a guildmate who has a newer update is online, it downloads in the
background and DisasterZone tells you. Type **`/dz update`** to install it (your interface reloads). Updates are
signed: your copy only takes the ones signed with this project's key.

A new zip is only needed when an update brings new art or new folders (the release notes say so).

## Discord

The guild's Discord bot (DisasterZoneTBC) takes raid sign-ups and BiS changes. They reach your game through the
DisasterZone Launcher 0.6.0: link it once with `/launcher` in Discord. The launcher only does Discord sync; the addon
itself comes from this page.

<p align="center"><img src="assets/divider.png" width="70%" alt=""></p>

## Credits

DisasterZone was created by **Tsumil** ([tsumilo](https://github.com/tsumilo)) for &lt;Casual Disaster&gt;, in
[tsumilo/DisasterZone-dev](https://github.com/tsumilo/DisasterZone-dev) and
[tsumilo/DisasterZone-releases](https://github.com/tsumilo/DisasterZone-releases), and handed over in November 2026.
It is maintained here by **Arakis** since 1.6.0. Thank you, Tsumi.

The item data is generated from **AtlasLoot Classic** (GPL v2). Libraries, data sources and art credits are listed in
`DisasterZone\NOTICE.md` inside the addon. World of Warcraft names, IDs and game art belong to Blizzard
Entertainment.

<details>
  <summary><b>What is in this repository</b></summary>
  <br>

  - Branch `main` (this page): the release tree as it was at 1.5.5 (`channels/`, `objects/`, the launcher), kept
    for history. Releases are on the [Releases page](https://github.com/Atredies/DisasterZone/releases).
  - Branch `dev`: the addon's source, its test harness and tools; docs in `_DisasterZone-vault/`.
  - Branch `upstream-1.6.0`: the original author's unreleased work after 1.5.5, kept for reference.
</details>

<details>
  <summary><b>License</b></summary>
  <br>

  The launcher's source (`launcher/`) is under the [MIT License](launcher/LICENSE).
</details>

<p align="center">
  <br>
  <img src="launcher/src-tauri/icons/128x128.png" width="56" alt="DisasterZone seal"><br>
  <sub>Made for &lt;Casual Disaster&gt;</sub>
</p>
