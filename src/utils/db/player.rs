use crate::impl_string_utils;
use crate::utils::db::{loadout::RawLoadoutData, Loadout};
use crate::utils::misc;
use crate::utils::misc::{ModelError, NFKind};
use mysql::Error;
use regex::Regex;
use std::backtrace::Backtrace;
use std::collections::HashMap;
use unicode_segmentation::UnicodeSegmentation;

impl_string_utils!();

lazy_static! {
    static ref FCRE: Regex = Regex::new(r"\D").unwrap();
    static ref RANKRE: Regex = Regex::new(r"(([ABC][-+ ]?)|(S\+[0-9]?)|S|(X [0-9]{0,4}))").unwrap();
}

static SR_RANK_ARRAY: [&str; 6] = [
    "intern",
    "apprentice",
    "part-timer",
    "go-getter",
    "overachiever",
    "profreshional",
];

#[derive(Debug)]
pub struct Player {
    id: u64,
    friend_code: String,
    ign: String,
    pub level: i32,
    sz: String,
    tc: String,
    rm: String,
    cb: String,
    sr: String,
    position: i16,
    loadout: Loadout,
    team_id: Option<u64>,
    free_agent: bool,
    is_private: bool,
}

impl Player {
    pub fn add_to_db(user_id: u64) -> Result<u64, Error> {
        misc::get_db_connection()
            .prep_exec(
                include_str!("../../../data/statements/player/insert.sql"),
                (user_id,),
            )
            .map(|x| x.last_insert_id())
    }
    pub fn from_db(user_id: u64) -> Result<Player, ModelError> {
        let result = match misc::get_db_connection().first_exec::<_, _, mysql::Row>(
            include_str!("../../../data/statements/player/select.sql"),
            (user_id,),
        ) {
            Ok(v) => v,
            Err(e) => {
                return Err(ModelError::Database(
                    format!("Error in player data retrieval: {:#?}", e),
                    Backtrace::capture(),
                ))
            }
        };
        let row = match result {
            None => {
                return Err(ModelError::NotFound(
                    NFKind::Player(user_id),
                    Backtrace::capture(),
                ))
            }
            Some(v) => v,
        };

        let lv: i32 = row.get(0).unwrap();
        let dt: String = row.get(1).unwrap();
        let loadout = match Loadout::from_raw(match RawLoadoutData::parse(dt.as_str()) {
            Ok(v) => v,
            Err(e) => return Err(e),
        }) {
            Ok(v) => v,
            Err(e) => return Err(e),
        };

        Ok(Player {
            id: row.get("id").unwrap(),
            friend_code: row.get("friend_code").unwrap(),
            ign: row.get("ign").unwrap(),
            level: lv,
            sz: row.get("sz").unwrap(),
            tc: row.get("tc").unwrap(),
            rm: row.get("rm").unwrap(),
            cb: row.get("cb").unwrap(),
            sr: row.get("sr").unwrap(),
            position: row.get("position").unwrap(),
            loadout,
            team_id: row.get("team_id").unwrap(),
            free_agent: row.get("free_agent").unwrap(),
            is_private: row.get("is_private").unwrap(),
        })
    }
    pub fn id(&self) -> &u64 {
        &self.id
    }
    pub fn fc(&self) -> &String {
        &self.friend_code
    }
    pub fn set_fc(&mut self, fc_string: &str) -> Result<(), ()> {
        let regexed = FCRE.replace_all(fc_string, "");

        if regexed.len() == 12 {
            let f1 = regexed.substring(0, 4);
            let f2 = regexed.substring(4, 4);
            let f3 = regexed.substring(8, 4);
            self.friend_code = format!("SW-{}-{}-{}", f1, f2, f3);
        } else {
            return Err(());
        }

        Ok(())
    }
    pub fn name(&self) -> &String {
        &self.ign
    }
    pub fn set_name(&mut self, name: String) -> Result<(), ()> {
        let __name__ = UnicodeSegmentation::graphemes(name.as_str(), true).collect::<Vec<&str>>();

        if __name__.len() > 10 || __name__.is_empty() {
            return Err(());
        } else {
            self.ign = name;
        }
        Ok(())
    }
    pub fn ranks(&self) -> HashMap<&'static str, &String> {
        let mut hm = HashMap::new();
        hm.insert("Splat Zones", &self.sz);
        hm.insert("Tower Control", &self.tc);
        hm.insert("Rainmaker", &self.rm);
        hm.insert("Clam Blitz", &self.cb);
        hm.insert("Salmon Run", &self.sr);
        hm
    }
    pub fn set_rank(&mut self, mode: &str, rank: &str) -> Result<(), ModelError> {
        match mode {
            "sz" | "splat_zones" | "sz_rank" => {
                if !RANKRE.is_match(rank) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank
                    )));
                }
                self.sz = rank.to_ascii_uppercase()
            }
            "tc" | "tower_control" | "tc_rank" => {
                if !RANKRE.is_match(rank) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank
                    )));
                }
                self.tc = rank.to_ascii_uppercase()
            }
            "rm" | "rainmaker" | "rm_rank" => {
                if !RANKRE.is_match(rank) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank
                    )));
                }
                self.rm = rank.to_ascii_uppercase()
            }
            "cb" | "clam_blitz" | "cb_rank" => {
                if !RANKRE.is_match(rank) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank
                    )));
                }
                self.cb = rank.to_ascii_uppercase()
            }
            "sr" | "salmon_run" | "sr_rank" => {
                for static_rank in &SR_RANK_ARRAY {
                    if &(rank.to_ascii_lowercase()) == static_rank {
                        use heck::TitleCase;

                        self.sr = rank.to_title_case().replace(' ', "-");
                        return Ok(());
                    }
                }
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid Salmon Run Rank: {}",
                    rank
                )));
            }
            _ => {
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid Mode: {}",
                    mode
                )))
            }
        }
        Ok(())
    }

    pub fn pos(&self) -> &'static str {
        misc::pos_map().get(&self.position).unwrap()
    }
    pub fn set_pos(&mut self, pos_int: i16) -> Result<(), ()> {
        let pos_map = misc::pos_map();
        for key in pos_map.keys() {
            if key == &pos_int {
                self.position = pos_int;
                return Ok(());
            }
        }
        Err(())
    }

    pub fn loadout(&self) -> &Loadout {
        &self.loadout
    }
    pub fn set_loadout(&mut self, hex: &str) -> Result<(), ModelError> {
        let raw = match RawLoadoutData::parse(hex) {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        match Loadout::from_raw(raw) {
            Ok(v) => self.loadout = v,
            Err(e) => return Err(e),
        }
        Ok(())
    }
    #[allow(dead_code)] // Only for now, while teams are still being implemented.
    pub fn team_id(&self) -> &Option<u64> {
        &self.team_id
    }
    pub fn set_team_id(&mut self, team_id: Option<u64>) {
        self.team_id = team_id;
    }
    pub fn is_free_agent(&self) -> &bool {
        &self.free_agent
    }
    pub fn set_free_agent(&mut self, response: &str) -> Result<&bool, ModelError> {
        let tmp = response.to_ascii_lowercase();
        let r = tmp.as_str();

        match r {
            "ok" | "yes" | "true" | "1" => self.free_agent = true,
            "no" | "false" | "0" => self.free_agent = false,
            _ => {
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid response: `{}`",
                    response
                )))
            }
        }

        Ok(&self.free_agent)
    }

    pub fn is_private(&self) -> &bool {
        &self.is_private
    }
    pub fn set_private(&mut self, response: &str) -> Result<&bool, ModelError> {
        let tmp = response.to_ascii_lowercase();
        let r = tmp.as_str();

        match r {
            "ok" | "yes" | "true" | "1" => self.is_private = true,
            "no" | "false" | "0" => self.is_private = false,
            _ => {
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid response: `{}`",
                    response
                )))
            }
        }

        Ok(&self.is_private)
    }
    pub fn update(&self) -> Result<u64, Error> {
        use mysql::params;
        misc::get_db_connection()
            .prep_exec(
                include_str!("../../../data/statements/player/update.sql"),
                params! {
                    "fc" => &self.friend_code,
                    "name" => &self.ign,
                    "lv" => self.level,
                    "sz" => &self.sz,
                    "tc" => &self.tc,
                    "rm" => &self.rm,
                    "cb" => &self.cb,
                    "sr" => &self.sr,
                    "pos" => self.position,
                    "ld" => self.loadout.raw().hex(),
                    "tid" => self.team_id,
                    "isp" => self.is_private,
                    "fa" => self.free_agent,
                    "id" => self.id,
                },
            )
            .map(|x| x.last_insert_id())
    }
}
