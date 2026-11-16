//! The launcher's own settings (one JSON file in the OS config folder).

use super::error::{msg, Result};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;

/// Where releases are published (the public releases repository). A setting can point elsewhere for testing.
pub const DEFAULT_SOURCE: &str = include_str!("../../../source.txt");

/// What an install, update or release check says while the release source is still upstream's.
pub const NO_RELEASE_SOURCE: &str =
    "Addon updates are off in this launcher for now: there is no DisasterZone release feed of ours yet. Update the addon from the releases page; Discord sync works as before.";

/// A URL that still points at upstream's releases repository (tsumilo/DisasterZone-releases): its manifests carry the
/// original 1.5.5 release, signed with a key we don't hold, so installing from it would put that old addon back over a
/// newer one. The launcher never installs, updates or auto-installs from it; the guard falls away once source.txt
/// names a feed of ours.
pub fn is_upstream_source(url: &str) -> bool {
    url.to_ascii_lowercase().contains("tsumilo/disasterzone-releases")
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default, rename_all = "camelCase")]
pub struct Settings {
    pub wow_root: Option<String>,
    pub flavor: String,
    pub channel: String,
    /// highest manifest seq seen per channel: an older manifest is refused (replayed or stale)
    pub seen_seq: BTreeMap<String, u64>,
    /// after a restore: do not offer the newest release until the user asks
    pub hold: bool,
    pub keep_backups: usize,
    pub check_on_start: bool,
    /// override of DEFAULT_SOURCE (a URL or a folder)
    pub source: Option<String>,
    /// Battle.net product code for Play (e.g. "WoWC"): empty = just open Battle.net
    pub launch_code: String,
    /// Linux (or any OS): a shell command Play runs instead of Battle.net, e.g. "lutris lutris:rungame/battlenet"
    pub play_command: String,
    /// opt-in: closing the window keeps the launcher in the tray, checking every 5 minutes
    pub tray: bool,
    /// opt-in (needs tray): install a new release in the background while WoW is closed
    pub auto_install: bool,
    /// opt-in (needs tray): start hidden in the tray when the user logs in
    pub autostart: bool,
    /// highest seq a notification was shown for, per channel (one notification per release)
    pub notified_seq: BTreeMap<String, u64>,
    /// launcher version the "a new launcher is ready" notification was shown for
    pub notified_launcher: String,
    /// the "still running in the tray" hint was shown once
    pub tray_hint_shown: bool,
    /// set before the launcher restarts after updating itself in the background: start hidden in the tray
    pub start_hidden_once: bool,
    /// Discord sync: the bot's server (empty = sync::DEFAULT_SERVER)
    pub sync_server: String,
    /// the Discord name this PC's member key belongs to (the key itself is in the OS credential store)
    pub sync_user: String,
    /// pack id -> keep it (the Games tab, the picker, the 3D rooms switch), for the game version in `flavor`. A pack
    /// with no entry is kept when its folder is installed or it is on by default (install.rs wanted()).
    pub packs: BTreeMap<String, bool>,
    /// the one-time games picker was answered for this game version (until then the tray doesn't install a release
    /// with games)
    pub packs_picked: bool,
    /// every game version's own choices, by flavor folder: switching versions (set_flavor) puts the other version's
    /// in `packs` / `packsPicked`, which stay the current version's (launchers before 0.5.0 read only those). Before
    /// 0.5.0 one list served every version: a game left out in Classic Era showed as leaving Anniversary too.
    pub flavor_packs: BTreeMap<String, FlavorPacks>,
    /// Settings > Discord "Show me as in game": the guild's "online now" lists this PC's game (sync.rs)
    pub show_presence: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            wow_root: None,
            flavor: "_anniversary_".into(),
            channel: "stable".into(),
            seen_seq: BTreeMap::new(),
            hold: false,
            keep_backups: 3,
            check_on_start: true,
            source: None,
            launch_code: String::new(),
            play_command: String::new(),
            tray: false,
            auto_install: false,
            autostart: false,
            notified_seq: BTreeMap::new(),
            notified_launcher: String::new(),
            tray_hint_shown: false,
            start_hidden_once: false,
            sync_server: String::new(),
            sync_user: String::new(),
            packs: BTreeMap::new(),
            packs_picked: false,
            flavor_packs: BTreeMap::new(),
            show_presence: true,
        }
    }
}

/// One game version's game choices (Settings::flavor_packs).
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(default, rename_all = "camelCase")]
pub struct FlavorPacks {
    pub packs: BTreeMap<String, bool>,
    pub picked: bool,
}

impl Settings {
    pub fn source(&self) -> String {
        self.source.clone().filter(|s| !s.trim().is_empty()).unwrap_or_else(|| DEFAULT_SOURCE.trim().to_string())
    }

    /// The source an install, update or release check reads: refused while it is upstream's (is_upstream_source), for
    /// every game version. A folder or another URL (a test feed, our own later) is used as before.
    pub fn release_source(&self) -> Result<String> {
        let src = self.source();
        if is_upstream_source(&src) {
            return msg(NO_RELEASE_SOURCE);
        }
        Ok(src)
    }

    pub fn flavor_dir(&self) -> Option<PathBuf> {
        self.wow_root.as_ref().map(|r| PathBuf::from(r).join(&self.flavor))
    }

    /// Switch the game version: its own game choices come in (none yet: nothing chosen, so installed games stay and
    /// the picker asks once when a release brings games); the old version's wait for when it comes back.
    pub fn set_flavor(&mut self, flavor: String) {
        if flavor == self.flavor {
            return;
        }
        let old = FlavorPacks { packs: std::mem::take(&mut self.packs), picked: self.packs_picked };
        self.flavor_packs.insert(std::mem::replace(&mut self.flavor, flavor), old);
        let new = self.flavor_packs.get(&self.flavor).cloned().unwrap_or_default();
        self.packs = new.packs;
        self.packs_picked = new.picked;
    }
}

fn path() -> PathBuf {
    dirs::config_dir().unwrap_or_else(std::env::temp_dir).join("DisasterZoneLauncher").join("settings.json")
}

pub fn load() -> Settings {
    // (a file saved by a Windows editor may start with a byte-order mark, which serde_json refuses)
    fs::read(path())
        .ok()
        .and_then(|d| serde_json::from_slice(d.strip_prefix(b"\xEF\xBB\xBF").unwrap_or(&d)).ok())
        .unwrap_or_default()
}

pub fn save(s: &Settings) -> Result<()> {
    let p = path();
    fs::create_dir_all(p.parent().unwrap())?;
    let tmp = p.with_extension("tmp");
    // (the current version's choices are kept with the others too: set_flavor finds them there when it comes back)
    let mut s = s.clone();
    s.flavor_packs.insert(s.flavor.clone(), FlavorPacks { packs: s.packs.clone(), picked: s.packs_picked });
    fs::write(&tmp, serde_json::to_vec_pretty(&s).unwrap())?;
    fs::rename(&tmp, &p)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn upstreams_release_source_is_refused() {
        let upstream = "https://raw.githubusercontent.com/tsumilo/DisasterZone-releases/main/";
        assert!(is_upstream_source(upstream));
        assert!(is_upstream_source("https://raw.githubusercontent.com/TSUMILO/DisasterZone-Releases/main"));
        assert!(!is_upstream_source("https://raw.githubusercontent.com/Atredies/DisasterZone/main/"));
        for flavor in ["_anniversary_", "_classic_era_", "_retail_"] {
            let s = Settings { flavor: flavor.into(), source: Some(upstream.into()), ..Default::default() };
            assert_eq!(s.release_source().unwrap_err().to_string(), NO_RELEASE_SOURCE);
        }
        let ours = "https://example.org/dz-releases/";
        let s = |src: &str| Settings { source: Some(src.into()), ..Default::default() };
        assert_eq!(s(ours).release_source().unwrap(), ours);
        assert_eq!(s("/home/me/dz-build").release_source().unwrap(), "/home/me/dz-build");
        // (the built-in source as shipped: refused while source.txt is upstream's)
        let built_in = Settings { source: None, ..Default::default() };
        assert_eq!(built_in.release_source().is_err(), is_upstream_source(DEFAULT_SOURCE));
    }

    #[test]
    fn each_game_version_keeps_its_own_game_choices() {
        let mut s = Settings { flavor: "_classic_era_".into(), ..Default::default() };
        s.packs.insert("azeromon".into(), true);
        s.packs.insert("chess".into(), false);
        s.packs_picked = true;
        // Anniversary never chose: nothing chosen there (its installed games stay), the picker may ask
        s.set_flavor("_anniversary_".into());
        assert!(s.packs.is_empty() && !s.packs_picked);
        s.packs.insert("chess".into(), true);
        // back to Classic Era: its own choices, untouched by Anniversary's
        s.set_flavor("_classic_era_".into());
        assert_eq!(s.packs.get("chess"), Some(&false));
        assert_eq!(s.packs.get("azeromon"), Some(&true));
        assert!(s.packs_picked);
        s.set_flavor("_anniversary_".into());
        assert_eq!(s.packs.get("chess"), Some(&true));
        // a file written by a launcher before 0.5.0 (no flavorPacks): its list is the current version's
        let old: Settings = serde_json::from_str(r#"{"flavor":"_anniversary_","packs":{"bingo":false},"packsPicked":true}"#).unwrap();
        assert_eq!(old.packs.get("bingo"), Some(&false));
        assert!(old.packs_picked && old.flavor_packs.is_empty());
    }
}
